import os
import logging
from logging import Logger
from typing import Final

from django.conf import settings
from django.core.management import call_command
from django.core.cache import cache
from django.db.models.query import QuerySet
from django.utils import timezone

from member.models import Person

from . import constants
from .google import GoogleDriveService, FileResources, MIME_TYPE
from .models import AuditEntry, Parameter
from .parameters import getParameterValue

logger: Logger = logging.getLogger(constants.LOGGERS.MAIN)


def setMagicNumber() -> None:
    """
    # ------------------------------------------------------------- #
    # This is the last object that is not included of the specified #
    # period of allowed logged in attempts reset                    #
    # Ex. if the parameter 'ALLOWED_LOGGED_IN_ATTEMPTS_RESET'       #
    # set to 7 days, the last object that will be reset, It will be #
    # saved in the in 'MAGIC_NUMBER' parameter, to make the search  #
    # in the table 'AuditEntry' faster and more scalable            #
    # ------------------------------------------------------------- #
    """
    logger.info('=========== CRON START SETTING MAGIC NUMBER ===========')
    magic_number: int = getParameterValue(constants.PARAMETERS.MAGIC_NUMBER)
    reset_days: int = getParameterValue(
        constants.PARAMETERS.ALLOWED_LOGGED_IN_ATTEMPTS_RESET)
    last_audit_entry: QuerySet[AuditEntry] = AuditEntry.filter(
        id__gte=magic_number,
        created__range=(timezone.now() - timezone.timedelta(days=reset_days),
                        timezone.now()))
    try:
        magic_number = last_audit_entry[0].id
    except IndexError:
        try:
            magic_number = AuditEntry.getLastInsertedObject().id
        except AttributeError:
            magic_number = 1

    # cleanup unsuspicious post requests
    normal_posts: QuerySet[AuditEntry] = AuditEntry.filter(
        id__lt=magic_number,
        action=constants.ACTION.NORMAL_POST)
    for post in normal_posts:
        post.delete()

    # This is the only time which a parameter updated in code
    pram = Parameter.get(name=constants.PARAMETERS.MAGIC_NUMBER)
    pram.value = magic_number  # NOQA
    pram.save()
    # Reset the last audit entry cache
    cache.delete(constants.CACHE.LAST_AUDIT_ENTRY_QUERYSET)
    AuditEntry.getLastAuditEntry()
    logger.info(f'Magic Number Updated to [{magic_number}].')
    logger.info('=========== CRON FINISH SETTING MAGIC NUMBER ===========')


def DBBackup() -> None:
    logger.info('=========== CRON START DB BACKUP ===========')
    MAX_BACKUP_FILES: Final[int] = 4  # keep last 4 only
    try:
        options: dict[str, str] = {
            'servername': 'yemeni-community-indonesia',
            'exclude_tables': 'main_auditentry'
        }
        call_command('dbbackup', **options)

        folder_path = str(settings.BACKUP_FOLDER)
        files = [f for f in os.listdir(folder_path) if os.path.isfile(
            os.path.join(folder_path, f))]
        files.sort(key=lambda x: os.path.getmtime(
            os.path.join(folder_path, x)))

        files_to_remove = files[:int(f'-{MAX_BACKUP_FILES}')]

        for file in files_to_remove:
            os.remove(os.path.join(folder_path, file))
            logger.info(f"Database dumb file '{file}' has been DELETED.")

    except Exception as e:
        logger.exception(e)

    logger.info('=========== CRON FINISH DB BACKUP ===========')


def cleanupOldLogs() -> None:
    logger.info('=========== CRON START CLEANUP OLD LOGS ===========')

    try:
        MAX_LOGS_FILES: Final[int] = 30
        folder_path = str(settings.LOGS_PATH)
        files = [f for f in os.listdir(folder_path) if os.path.isfile(
            os.path.join(folder_path, f))]
        files.sort(key=lambda x: os.path.getmtime(
            os.path.join(folder_path, x)))

        files_to_remove = files[:int(f'-{MAX_LOGS_FILES}')]
        if not files_to_remove:
            logger.info("No old logs to remove.")

        for file in files_to_remove:
            os.remove(os.path.join(folder_path, file))
            logger.info(f"Log file '{file}' has been DELETED.")
    except Exception as e:
        logger.exception(e)

    logger.info('=========== CRON FINISH CLEANUP OLD LOGS ===========')


def uploadDBBackupToGoogleDrive() -> None:
    logger.info('=========== CRON START UPLOADING DB BACKUP ===========')
    fileService = None
    with GoogleDriveService() as googleDriveService:
        try:
            token: str = str(settings.BASE_DIR / 'data/google_client.json')
            googleDriveService.authenticate(token)
            if googleDriveService.credentials.valid:
                logger.info("Authenticated to Google Drive Successfully.")
            else:
                logger.error("Failed to authenticated to Google Drive.")
                return

            fileService = googleDriveService.fileService()

            folder_path = str(settings.BACKUP_FOLDER)
            files = [f for f in os.listdir(folder_path) if os.path.isfile(
                os.path.join(folder_path, f))]

            cloud_backup_folder_id: str = os.environ.get(
                "CloudDbBackupFolderId")
            if not cloud_backup_folder_id:
                logger.warning(
                    "'CloudDbBackupFolderId' Not registered in environment variables")
                backup_folder = fileService.createFolderIfDoesNotExists(
                    "db_backup")
                cloud_backup_folder_id = backup_folder.id
                os.environ["CloudDbBackupFolderId"] = cloud_backup_folder_id
                logger.info(
                    f"CloudDbBackupFolderId: {os.environ.get('CloudDbBackupFolderId')}")

            stat_time1 = timezone.now()
            for file in files:
                isFileExistsInCloud: str | None = fileService.getFileIdByFileName(
                    file_name=file,
                    parent_folder_id=cloud_backup_folder_id,
                    mime_type=MIME_TYPE.TXT
                )
                if isFileExistsInCloud:
                    logger.info(f"File '{file}' Already Exists in the cloud.")
                    continue

                stat_time2 = timezone.now()
                logger.info(f"Start Uploading File '{file}' to Cloud.")
                fileService.uploadFile(
                    file_name=file,
                    local_file_dir=folder_path,
                    mime_type=MIME_TYPE.TXT,
                    cloud_folder_id=cloud_backup_folder_id,
                    replace_if_exists=False)
                logger.info(f"Uploading File '{file}' to Cloud Completed.")
                logger.info(f"Uploading Time: {timezone.now() - stat_time2}")

            logger.info(f"Total Uploading Time: {timezone.now() - stat_time1}")

        except Exception as e:
            logger.exception(e)
        finally:
            if fileService:
                fileService.close()

    logger.info('=========== CRON FINISH UPLOADING DB BACKUP ===========')


def uploadPhotographs(fileService, queryset: QuerySet[Person]) -> int:
    # Photographs
    logger.info("Start Processing Photographs")
    photographs_folder_id: str = os.environ.get(
        "CloudPhotographsFolderId")
    if not photographs_folder_id:
        logger.warning(
            "'CloudPhotographsFolderId' Not registered in environment variables")
        documents_folder = fileService.createFolderIfDoesNotExists(
            "documents")
        images_folder = fileService.createFolderIfDoesNotExists(
            "images", documents_folder.id)
        photographs_folder = fileService.createFolderIfDoesNotExists(
            "photographs", images_folder.id)
        photographs_folder_id = photographs_folder.id
        os.environ["CloudPhotographsFolderId"] = photographs_folder_id
        logger.info(
            f"CloudPhotographsFolderId: {os.environ.get('CloudPhotographsFolderId')}")

    cloud_files: list[FileResources] = fileService.getDirectoryFileList(
        folder_id=photographs_folder_id,
        mime_type=MIME_TYPE.JPEG
    )
    local_files: list[str] = [
        person.photograph.name.rsplit('/', maxsplit=1).pop() for person in queryset
    ]

    file_resources_to_remove: list[FileResources] = []
    for file_resources in cloud_files:
        if len(local_files) == 0:
            break

        if file_resources.name in local_files:
            file_resources_to_remove.append(file_resources)
            local_files.remove(file_resources.name)

    for file_resources in file_resources_to_remove:
        cloud_files.remove(file_resources)

    count: int = 0
    for file in local_files:
        stat_time2 = timezone.now()
        logger.info(f"Start Uploading File '{file}' to Cloud.")
        fileService.uploadFile(
            file_name=file,
            local_file_dir=str(settings.MEDIA_ROOT /
                               constants.MEDIA_DIR.PHOTOGRAPHS_DIR),
            mime_type=MIME_TYPE.JPEG,
            cloud_folder_id=photographs_folder_id,
            replace_if_exists=False)
        logger.info(f"Uploading File '{file}' to Cloud Completed.")
        logger.info(f"Uploading Time: {timezone.now() - stat_time2}")
        count += 1

    for file_resources in cloud_files:
        logger.info(
            f"Deleting FIle '{file_resources.name}' from Google Drive.")
        fileService.delete(file_resources.id)

    return count


def uploadPassportsImages(fileService, queryset: QuerySet[Person]) -> int:
    # Passport Images
    logger.info("Start Processing Passport Images")
    passport_images_folder_id: str = os.environ.get(
        "CloudPassportImagesFolderId")
    if not passport_images_folder_id:
        logger.warning(
            "'CloudPassportImagesFolderId' Not registered in environment variables")
        documents_folder = fileService.createFolderIfDoesNotExists(
            "documents")
        images_folder = fileService.createFolderIfDoesNotExists(
            "images", documents_folder.id)
        passport_images_folder = fileService.createFolderIfDoesNotExists(
            "passportImages", images_folder.id)
        passport_images_folder_id = passport_images_folder.id
        os.environ["CloudPassportImagesFolderId"] = passport_images_folder_id
        logger.info(
            f"CloudPassportImagesFolderId: {os.environ.get('CloudPassportImagesFolderId')}")

    cloud_files: list[FileResources] = fileService.getDirectoryFileList(
        folder_id=passport_images_folder_id,
        mime_type=MIME_TYPE.JPEG
    )
    local_files: list[str] = [
        person.passport_photo.name.rsplit('/', maxsplit=1).pop() for person in queryset
    ]

    file_resources_to_remove: list[FileResources] = []
    for file_resources in cloud_files:
        if len(local_files) == 0:
            break

        if file_resources.name in local_files:
            file_resources_to_remove.append(file_resources)
            local_files.remove(file_resources.name)

    for file_resources in file_resources_to_remove:
        cloud_files.remove(file_resources)

    count: int = 0
    for file in local_files:
        stat_time2 = timezone.now()
        logger.info(f"Start Uploading File '{file}' to Cloud.")
        fileService.uploadFile(
            file_name=file,
            local_file_dir=str(settings.MEDIA_ROOT /
                               constants.MEDIA_DIR.PASSPORTS_DIR),
            mime_type=MIME_TYPE.JPEG,
            cloud_folder_id=passport_images_folder_id,
            replace_if_exists=False)
        logger.info(f"Uploading File '{file}' to Cloud Completed.")
        logger.info(f"Uploading Time: {timezone.now() - stat_time2}")
        count += 1

    for file_resources in cloud_files:
        logger.info(
            f"Deleting FIle '{file_resources.name}' from Google Drive.")
        fileService.delete(file_resources.id)

    return count


def uploadResidencyImages(fileService, queryset: QuerySet[Person]) -> int:
    # Residency Images
    logger.info("Start Processing Residency Images")
    residency_images_folder_id: str = os.environ.get(
        "CloudResidencyImagesFolderId")
    if not residency_images_folder_id:
        logger.warning(
            "'CloudResidencyImagesFolderId' Not registered in environment variables")
        documents_folder = fileService.createFolderIfDoesNotExists(
            "documents")
        images_folder = fileService.createFolderIfDoesNotExists(
            "images", documents_folder.id)
        residency_images_folder = fileService.createFolderIfDoesNotExists(
            "residencyImages", images_folder.id)
        residency_images_folder_id = residency_images_folder.id
        os.environ["CloudResidencyImagesFolderId"] = residency_images_folder_id
        logger.info(
            f"CloudResidencyImagesFolderId: {os.environ.get('CloudResidencyImagesFolderId')}")

    cloud_files: list[FileResources] = fileService.getDirectoryFileList(
        folder_id=residency_images_folder_id,
        mime_type=MIME_TYPE.JPEG
    )
    local_files: list[str] = [
        person.residency_photo.name.rsplit('/', maxsplit=1).pop() for person in queryset
    ]

    file_resources_to_remove: list[FileResources] = []
    for file_resources in cloud_files:
        if len(local_files) == 0:
            break

        if file_resources.name in local_files:
            file_resources_to_remove.append(file_resources)
            local_files.remove(file_resources.name)

    for file_resources in file_resources_to_remove:
        cloud_files.remove(file_resources)

    count: int = 0
    for file in local_files:
        stat_time2 = timezone.now()
        logger.info(f"Start Uploading File '{file}' to Cloud.")
        fileService.uploadFile(
            file_name=file,
            local_file_dir=str(settings.MEDIA_ROOT /
                               constants.MEDIA_DIR.RESIDENCY_IMAGES_DIR),
            mime_type=MIME_TYPE.JPEG,
            cloud_folder_id=residency_images_folder_id,
            replace_if_exists=False)
        logger.info(f"Uploading File '{file}' to Cloud Completed.")
        logger.info(f"Uploading Time: {timezone.now() - stat_time2}")
        count += 1

    for file_resources in cloud_files:
        logger.info(
            f"Deleting FIle '{file_resources.name}' from Google Drive.")
        fileService.delete(file_resources.id)

    return count


def uploadMembershipCardImages(fileService, queryset: QuerySet[Person]) -> int:
    # Membership Images
    logger.info("Start Processing Membership Images")
    membership_images_folder_id: str = os.environ.get(
        "CloudMembershipImagesFolderId")
    if not membership_images_folder_id:
        logger.warning(
            "'CloudMembershipImagesFolderId' Not registered in environment variables")
        documents_folder = fileService.createFolderIfDoesNotExists(
            "documents")
        images_folder = fileService.createFolderIfDoesNotExists(
            "images", documents_folder.id)
        membership_images_folder = fileService.createFolderIfDoesNotExists(
            "membershipImages", images_folder.id)
        membership_images_folder_id = membership_images_folder.id
        os.environ["CloudMembershipImagesFolderId"] = membership_images_folder_id
        logger.info(
            f"CloudMembershipImagesFolderId: {os.environ.get('CloudMembershipImagesFolderId')}")

    cloud_files: list[FileResources] = fileService.getDirectoryFileList(
        folder_id=membership_images_folder_id,
        mime_type=MIME_TYPE.JPEG
    )
    local_files: list[str] = [
        person.membership.membership_card.name.rsplit('/', maxsplit=1).pop()
        for person in queryset
        if person.membership and person.membership.membership_card
    ]

    file_resources_to_remove: list[FileResources] = []
    for file_resources in cloud_files:
        if len(local_files) == 0:
            break

        if file_resources.name in local_files:
            file_resources_to_remove.append(file_resources)
            local_files.remove(file_resources.name)

    for file_resources in file_resources_to_remove:
        cloud_files.remove(file_resources)

    count: int = 0
    for file in local_files:
        stat_time2 = timezone.now()
        logger.info(f"Start Uploading File '{file}' to Cloud.")
        fileService.uploadFile(
            file_name=file,
            local_file_dir=str(settings.MEDIA_ROOT /
                               constants.MEDIA_DIR.MEMBERSHIP_IMAGES_DIR),
            mime_type=MIME_TYPE.JPEG,
            cloud_folder_id=membership_images_folder_id,
            replace_if_exists=False)
        logger.info(f"Uploading File '{file}' to Cloud Completed.")
        logger.info(f"Uploading Time: {timezone.now() - stat_time2}")
        count += 1

    for file_resources in cloud_files:
        logger.info(
            f"Deleting FIle '{file_resources.name}' from Google Drive.")
        fileService.delete(file_resources.id)

    return count


def uploadDocumentsToGoogleDrive() -> None:
    logger.info('=========== CRON START UPLOADING Documents ===========')
    fileService = None
    with GoogleDriveService() as googleDriveService:
        try:
            token: str = str(settings.BASE_DIR / 'data/google_client.json')
            googleDriveService.authenticate(token)
            if googleDriveService.credentials.valid:
                logger.info("Authenticated to Google Drive Successfully.")
            else:
                logger.error("Failed to authenticated to Google Drive.")
                return

            stat_time1 = timezone.now()
            fileService = googleDriveService.fileService()
            queryset: QuerySet[Person] = Person.getAll()

            count = 0
            count += uploadPhotographs(fileService, queryset)
            count += uploadPassportsImages(fileService, queryset)
            count += uploadResidencyImages(fileService, queryset)
            count += uploadMembershipCardImages(fileService, queryset)

            if count:
                logger.info(f"{count} Total documents uploaded.")
                logger.info(
                    f"Total Uploading Time: {timezone.now() - stat_time1}")
            else:
                logger.info("Already up to date no files uploaded")

        except Exception as e:
            logger.exception(e)
        finally:
            if fileService:
                fileService.close()

    logger.info('=========== CRON FINISH UPLOADING Documents ===========')
