"""
* This is a module for interacting with the Google Drive and Google Form APIs. 
* 
* It allows you to authenticate with your Google Drive account, 
* and perform various actions such as creating and retrieving files and forms.
* 
* Please note that this module is not complete and may require additional functionality and error handling.
* 
* Created by: Mohammed Ba Karman
* E-Mail: msmabk11@gmail.com
* Version: 1.1.0
"""
import json
from pathlib import Path
from dataclasses import dataclass, field, fields
from datetime import datetime
from collections import namedtuple
from typing import Any, Final, Optional, Union
from os.path import isfile as isFileLocallyExist

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.discovery import Resource
from googleapiclient.http import MediaFileUpload


FILE_TYPE = namedtuple('str', [
    'AUDIO',
    'DOCUMENT',
    'FILE',
    'FOLDER',
    'PHOTO',
    'PRESENTATION',
    'SPREADSHEET',
    'UNKNOWN',
    'VIDEO',
    'FORM',
])(
    'application/vnd.google-apps.audio',
    'application/vnd.google-apps.document',
    'application/vnd.google-apps.file',
    'application/vnd.google-apps.folder',
    'application/vnd.google-apps.photo',
    'application/vnd.google-apps.presentation',
    'application/vnd.google-apps.spreadsheet',
    'application/vnd.google-apps.unknown',
    'application/vnd.google-apps.video',
    'application/vnd.google-apps.form',
)

MIME_TYPE = namedtuple('str', [
    'JPEG',
    'PNG',
    'TXT',
])(
    'image/jpeg',
    'image/png',
    'text/plain',
)

GOOGLE_FORM_ITEM_TYPE = namedtuple('str', [
    'PAGE_BREAK_ITEM',
    'QUESTION_ITEM',
    'QUESTION_GROUP_ITEM',
    'VIDEO_ITEM',
    'IMAGE_ITEM',
])(
    'pageBreakItem',
    'questionItem',
    'questionGroupItem',
    'videoItem',
    'imageItem',
)

GOOGLE_FORM_QUESTION_TYPE = namedtuple('str', [
    'TEXT_QUESTION',
    'CHOICE_QUESTION',
    'SCALE_QUESTION',
    'DATE_QUESTION',
    'TIME_QUESTION',
    'FILE_UPLOAD_QUESTION',
])(
    'textQuestion',
    'choiceQuestion',
    'scaleQuestion',
    'dateQuestion',
    'timeQuestion',
    'fileUploadQuestion',
)


@dataclass
class Permission:
    id: str
    type: str
    kind: str
    role: str
    displayName: str = None
    emailAddress: str = None
    photoLink: str = None

    def __init__(self, **kwargs):
        valid_fields = set(f.name for f in fields(Permission))
        valid_kwargs = {k: v for k, v in kwargs.items() if k in valid_fields}
        for key, value in valid_kwargs.items():
            object.__setattr__(self, key, value)


@dataclass
class FileResources:
    id: str
    name: str
    kind: str = None
    mimeType: str = None
    starred: bool = False
    createdTime: datetime = None
    modifiedTime: datetime = None
    permissions: list[Permission] = None
    owners: list[dict[str, Any]] = None
    isOwned: int = field(init=False)

    def __post_init__(self) -> None:
        self.isOwned = False
        for owner in self.owners:
            if owner.get("me") == True:
                self.isOwned = True
                break

    def __str__(self) -> str:
        main_str_presentation = f"ID: {self.id} | File Name: {self.name}"
        if self.kind:
            main_str_presentation += f" | kind: {self.kind}"
        if self.mimeType:
            main_str_presentation += f" | Mime Type: {self.mimeType}"
        if self.starred:
            main_str_presentation += f" | Starred: {self.starred}"
        return main_str_presentation


@dataclass
class FormAnswer:
    questionId: str
    textAnswers: str


@dataclass
class FormResponse:
    responseId: str
    createTime: datetime
    lastSubmittedTime: datetime
    answers: list[FormAnswer]
    respondentEmail: str = None


@dataclass
class GoogleFormInfo:
    title: str
    description: str = None
    documentTitle: str = None


@dataclass
class GoogleFormItem:
    itemId: str
    itemType: str
    title: str = ""
    description: str = ""
    questions: list['GoogleFormItem'] = None
    itemData: dict[str, Any] = None
    isCustom: bool = False
    index: int = 0

    def __init__(self, **kwargs):
        valid_fields = set(f.name for f in fields(GoogleFormItem))
        valid_kwargs = {k: v for k, v in kwargs.items() if k in valid_fields}
        for key, value in valid_kwargs.items():
            object.__setattr__(self, key, value)


@dataclass
class GoogleForm:
    formId: str
    info: GoogleFormInfo
    revisionId: str
    responderUri: str
    responserUriId: str
    settings: dict[str, Any] = None
    items: list[GoogleFormItem] = None
    linkedSheetId: str = None
    createdTime: datetime = None
    modifiedTime: datetime = None
    file: FileResources = None
    numberOfPages: int = field(init=False)
    numberOfQuestions: int = field(init=False)

    def __post_init__(self) -> None:
        if not self.items:
            self.numberOfPages = 0
            self.numberOfQuestions = 0
        else:
            self.numberOfPages = 1
            self.numberOfQuestions = 0
            for item in self.items:
                if item.itemType == GOOGLE_FORM_ITEM_TYPE.PAGE_BREAK_ITEM:
                    self.numberOfPages += 1
                else:
                    self.numberOfQuestions += 1

            if self.items[0].itemType == GOOGLE_FORM_ITEM_TYPE.PAGE_BREAK_ITEM:
                self.numberOfPages -= 1


class GoogleAuthenticationError(Exception):
    pass


class GoogleService:
    API_NAME: Final[str] = ''
    API_VERSION: Final[str] = ''
    SCOPES: Final[list[str]] = []

    def __init__(self) -> None:
        if not self.API_NAME or not self.API_VERSION or not self.SCOPES:
            raise ValueError(
                'Invalid service info, please setup correct API_NAME, API_VERSION, and SCOPES.')
        self.credentials = None
        self._Service = None

    def __enter__(self):
        return self

    def __exit__(self, *args, **kwargs):
        if self._Service:
            self._Service.close()

    def authenticate(self, auth_file_path: str):

        if not isFileLocallyExist(auth_file_path):
            raise FileNotFoundError(
                f"The auth file does not exist: '{auth_file_path}'")

        with open(auth_file_path, 'r') as token:
            self.credentials: Credentials = Credentials.from_authorized_user_info(
                json.load(token), self.SCOPES)

        if not self.credentials or not self.credentials.valid:
            if self.credentials and self.credentials.expired and self.credentials.refresh_token:
                print("Token Expired.")
                request: Request = Request()
                self.credentials.refresh(request)

                with open(auth_file_path, 'w') as token:
                    token.write(self.credentials.to_json())

                if self.credentials.valid:
                    print("Token Refreshed Successfully.")
                else:
                    raise GoogleAuthenticationError("Failed to refresh token.")
            else:
                raise GoogleAuthenticationError("Field to authenticate.")

        self._Service: Resource = build(
            self.API_NAME, self.API_VERSION, credentials=self.credentials)

    def _isAuthenticated(self):
        if not self.credentials:
            raise GoogleAuthenticationError(
                "Please authenticate before using the file service.")


class GoogleDriveService(GoogleService):

    API_NAME: Final[str] = 'drive'
    API_VERSION: Final[str] = 'v3'
    SCOPES: Final[list[str]] = [
        'https://www.googleapis.com/auth/drive'
    ]

    def about(self):
        self._isAuthenticated()
        about: Resource = self._Service.about()
        return self._About(about)

    def fileService(self):
        self._isAuthenticated()
        fileService: Resource = self._Service.files()
        return self._FileService(fileService)

    class _About:

        def __init__(self, about: Resource) -> None:
            self.about: Resource = about
            self.metadata: dict[str, Any] = {
                'fields': '*'
            }

        def isGoogleDriveAppInstalled(self) -> bool:
            self.metadata['fields'] = 'appInstalled'
            request: Request = self.about.get(**self.metadata)
            return request.execute().get('appInstalled')

        def getUserInfo(self) -> dict[str, Any]:
            self.metadata['fields'] = 'user'
            request: Request = self.about.get(**self.metadata)
            return request.execute()

        def getStorageQuota(self) -> dict[str, Any]:
            self.metadata['fields'] = 'storageQuota'
            request: Request = self.about.get(**self.metadata)
            return request.execute()

        def getImportFormats(self) -> dict[str, Any]:
            self.metadata['fields'] = 'importFormats'
            request: Request = self.about.get(**self.metadata)
            return request.execute()

        def getMaxImportSizes(self) -> dict[str, Any]:
            self.metadata['fields'] = 'maxImportSizes'
            request: Request = self.about.get(**self.metadata)
            return request.execute()

        def getMaxUploadSize(self) -> dict[str, Any]:
            self.metadata['fields'] = 'maxUploadSize'
            request: Request = self.about.get(**self.metadata)
            return request.execute()

        def getFolderColorPalette(self) -> dict[str, Any]:
            self.metadata['fields'] = 'folderColorPalette'
            request: Request = self.about.get(**self.metadata)
            return request.execute()

        def getTeamDriveThemes(self) -> dict[str, Any]:
            self.metadata['fields'] = 'teamDriveThemes'
            request: Request = self.about.get(**self.metadata)
            return request.execute()

        def canCreateTeamDrives(self) -> bool:
            self.metadata['fields'] = 'canCreateTeamDrives'
            request: Request = self.about.get(**self.metadata)
            return request.execute().get('canCreateTeamDrives')

        def canCreateDrives(self) -> bool:
            self.metadata['fields'] = 'canCreateTeamDrives'
            request: Request = self.about.get(**self.metadata)
            return request.execute().get('canCreateTeamDrives')

        def close(self) -> None:
            self.about.close()

    class _FileService:

        def __init__(self, fileService: Resource) -> None:
            self.fileService: Resource = fileService

        def getFile(self, file_id) -> Union[FileResources, None]:
            metadata: dict[str, Any] = {'fileId': file_id}
            try:
                response: dict[str, Any] = self.fileService.get(
                    **metadata).execute()
                return FileResources(**response)
            except HttpError as error:
                error_content = json.loads(error.content)
                if error_content['error']['code'] == 404:
                    return None
                else:
                    raise error

        def createFolderIfDoesNotExists(self, folder_name: str, parent_folder_id: Optional[str | None] = None) -> FileResources:
            metadata: dict[str, Any] = {
                'body': {
                    'name': folder_name,
                    'mimeType': FILE_TYPE.FOLDER,
                }
            }

            folder_id: str = self.getFileIdByFileName(
                folder_name, parent_folder_id, FILE_TYPE.FOLDER)
            if folder_id:
                return self.getFile(folder_id)

            if parent_folder_id:
                metadata['body']['parents'] = [parent_folder_id]

            response: dict[str, Any] = self.fileService.create(
                **metadata).execute()
            file = FileResources(**response)

            return file

        def getFileIdByFileName(self, file_name: str, parent_folder_id: Optional[str | None] = None, mime_type: Optional[str | None] = None) -> Union[str, None]:
            file_id: str = None
            metadata = {
                'fields': 'nextPageToken, files(name, id)',
                'q': f"name='{file_name}' ",
                'spaces': 'drive'
            }

            if mime_type:
                metadata['q'] += f"and mimeType='{mime_type}' "

            if parent_folder_id:
                metadata['q'] += f"and parents='{parent_folder_id}' "

            file_list = self.fileService.list(**metadata)
            response: dict[str, Any] = file_list.execute()

            if len(response.get('files')):
                file_resources: FileResources = FileResources(
                    **response.get('files')[0])
                file_id = file_resources.id

            return file_id

        def getDirectoryFileList(self, folder_id: str, mime_type: Optional[str | None] = None) -> list[FileResources]:
            metadata = {
                'fields': 'nextPageToken, files(name, id, mimeType)',
                'q': f"parents='{folder_id}'",
                'spaces': 'drive'
            }

            if mime_type:
                metadata['q'] += f" and mimeType='{mime_type}' "

            next_page_token: str = "Start"
            file_list: list[FileResources] = []
            while next_page_token:
                response: dict[str, Any] = self.fileService.list(
                    **metadata).execute()

                next_page_token = response.get('nextPageToken')
                metadata['pageToken'] = next_page_token

                for file_data in response.get('files'):
                    file_list.append(FileResources(**file_data))

            return file_list

        def uploadFile(self, file_name: str, local_file_dir: str, mime_type: str, cloud_folder_id: Optional[str | None] = None, replace_if_exists: Optional[bool] = False) -> FileResources:
            file_full_path_local = str(Path(local_file_dir) / file_name)
            if not isFileLocallyExist(file_full_path_local):
                raise FileNotFoundError(
                    f"The file '{file_name}' does not exist in the provided directory '{local_file_dir}'")

            if cloud_folder_id and not self.getFile(cloud_folder_id):
                raise ValueError(
                    f"The specified folder with ID '{cloud_folder_id}' could not be found in the cloud.")

            file_id = self.getFileIdByFileName(
                file_name, cloud_folder_id, mime_type)
            if file_id:
                file = self.getFile(file_id)
                if not replace_if_exists:
                    return file

                self.delete(file.id)

            metadata: dict[str, Any] = {
                'body': {
                    'name': file_name
                },
                'media_body': MediaFileUpload(
                    file_full_path_local,
                    mimetype=mime_type
                )
            }

            if cloud_folder_id:
                metadata['body']['parents'] = [cloud_folder_id]

            response: dict[str, Any] = self.fileService.create(
                **metadata).execute()
            file = FileResources(**response)

            return file

        def delete(self, file_Id: str) -> None:
            metadata = {
                'fileId': file_Id
            }
            try:
                self.fileService.delete(**metadata).execute()
            except:
                print("File Does Not Exists")

        def emptyTrash(self) -> None:
            self.fileService.emptyTrash().execute()

        def close(self) -> None:
            self.fileService.close()


class GoogleFormsService(GoogleService):

    API_NAME: Final[str] = 'forms'
    API_VERSION: Final[str] = 'v1'
    SCOPES: Final[list[str]] = [
        'https://www.googleapis.com/auth/drive',
        'https://www.googleapis.com/auth/drive.file',
        'https://www.googleapis.com/auth/drive.readonly',
        'https://www.googleapis.com/auth/forms.body',
        'https://www.googleapis.com/auth/forms.body.readonly',
        'https://www.googleapis.com/auth/forms.responses.readonly',
    ]

    def __exit__(self, *args, **kwargs):
        if self._Service:
            self._Service.close()
            self.formsService.close()
            self.driveService.close()

    def formService(self):
        self._isAuthenticated()
        self.formsService: Resource = self._Service.forms()
        self.driveService: Resource = build(
            GoogleDriveService.API_NAME,
            GoogleDriveService.API_VERSION,
            credentials=self.credentials)
        fileService: Resource = self.driveService.files()
        permissionsService: Resource = self.driveService.permissions()
        return self._FormsService(self.formsService, fileService, permissionsService)

    class _FormsService:

        def __init__(self, formsService: Resource, fileService: Resource, permissionsService: Resource) -> tuple[str, str]:
            self.formsService: Resource = formsService
            self.fileService: Resource = fileService
            self.permissionsService: Resource = permissionsService

        def getForm(self, formId: str) -> GoogleForm:
            metaData: dict[str, str] = {"formId": formId}
            try:
                response: dict[str, Any] = self.formsService.get(
                    **metaData).execute()
                return self._mapForm(response)
            except HttpError as error:
                error_content = json.loads(error.content)
                if error_content['error']['code'] == 404:
                    return None
                else:
                    raise error

        def getFormTitle(self, formId: str) -> GoogleForm:
            metaData: dict[str, str] = {
                "formId": formId, "fields": "info(title)"}
            try:
                response: dict[str, Any] = self.formsService.get(
                    **metaData).execute()
                return response["info"]["title"]
            except HttpError as error:
                error_content = json.loads(error.content)
                if error_content['error']['code'] == 404:
                    return None
                else:
                    raise error

        def getFormsList(self) -> list[GoogleForm]:
            metadata: dict[str, str] = {
                'fields': 'nextPageToken, files(name, id, createdTime, modifiedTime, owners(me), '
                + 'permissions(id, type, kind, role, displayName, emailAddress, photoLink)) ',
                'q': f"mimeType='{FILE_TYPE.FORM}'",
                'spaces': 'drive'
            }

            next_page_token: str = "Start"
            forms_file_list: list[FileResources] = []
            date_format: str = "%Y-%m-%dT%H:%M:%S.%fZ"
            while next_page_token:
                response: dict[str, Any] = self.fileService.list(
                    **metadata).execute()

                next_page_token = response.get('nextPageToken')
                metadata['pageToken'] = next_page_token

                for file_data in response.get('files'):
                    file_data["createdTime"] = datetime.strptime(
                        file_data.get("createdTime"), date_format)
                    file_data["modifiedTime"] = datetime.strptime(
                        file_data.get("modifiedTime"), date_format)
                    permissions: list[Permission] = []
                    for permission in file_data.get("permissions"):
                        permissions.append(Permission(**permission))
                    file_data["permissions"] = permissions
                    forms_file_list.append(FileResources(**file_data))

            forms_list: list[GoogleForm] = []
            for form_file in forms_file_list:
                form: GoogleForm = None
                try:
                    form = self.getForm(form_file.id)
                    form.createdTime = form_file.createdTime
                    form.modifiedTime = form_file.modifiedTime
                    form.file = form_file
                except NotImplementedError:
                    ...
                forms_list.append(form)
            return forms_list

        def createForm(self, title: str) -> str:
            if not title:
                raise ValueError("Title cannot be empty!")

            body: dict[str, Any] = {
                "info": {
                    "title": title,
                    "documentTitle": title,
                }
            }

            response: dict[str, Any] = self.formsService.create(
                body=body).execute()
            return response.get("formId")

        def convertFormToQuiz(self, formId):
            body = {
                "requests": [
                    {
                        "updateSettings": {
                            "settings": {"quizSettings": {"isQuiz": True}},
                            "updateMask": "quizSettings.isQuiz",
                        }
                    }
                ]
            }
            response: dict[str, Any] = self.formsService.batchUpdate(
                formId=formId, body=body).execute()
            return response

        def addUserPermissionToForm(self, formId: str, user_email_address: str) -> None:
            metadata: dict[str, str] = {
                'type': 'user',
                'role': 'writer',
                'emailAddress': user_email_address,
            }

            self.permissionsService.create(
                fileId=formId, body=metadata).execute()

        def removeUserPermissionToForm(self, formId: str, permissionId: str) -> None:
            self.permissionsService.delete(
                fileId=formId, permissionId=permissionId).execute()

        def updateForm(self, formId: str, title: str = None, description: str = None, documentTitle: str = None):
            if not title and not description and not documentTitle:
                return

            info: dict[str, str] = {}
            updateMask: str = ""

            if title:
                info["title"] = title
                updateMask = "title"

            if description:
                info["description"] = description
                if updateMask:
                    updateMask += ", description"
                else:
                    updateMask = "description"

            if documentTitle:
                info["documentTitle"] = documentTitle
                if updateMask:
                    updateMask += ", documentTitle"
                else:
                    updateMask = "documentTitle"

            body = {
                "requests": [
                    {
                        "updateFormInfo": {
                            "info": info,
                            "updateMask": updateMask,
                        }
                    }
                ]
            }

            response: dict[str, Any] = self.formsService.batchUpdate(
                formId=formId, body=body).execute()
            return response

        def deleteForm(self, formId) -> None:
            self.fileService.delete(fileId=formId).execute()

        def getFormResponses(self, formId: str, questions_order: Optional[list[str] | None] = None) -> list[FormResponse]:
            try:
                response: dict[str, Any] = self.formsService.responses().list(
                    formId=formId).execute()
                responses: list[FormResponse] = []
                for response in response.get("responses", []):
                    responses.append(self._mapFormResponse(
                        response, questions_order))

                return responses
            except HttpError as error:
                error_content = json.loads(error.content)
                if error_content['error']['code'] == 404:
                    return None
                else:
                    raise error

        def getResponse(self, formId: str, responseId: str) -> FormResponse:
            metaData: dict[str, str] = {
                "formId": formId, "responseId": responseId}
            try:
                response: dict[str, Any] = self.formsService.responses().get(
                    **metaData).execute()
                return self._mapFormResponse(response)
            except HttpError as error:
                error_content = json.loads(error.content)
                if error_content['error']['code'] == 404:
                    return None
                else:
                    raise error

        def _mapForm(self, response: dict[str, Any]) -> GoogleForm:
            response["info"] = GoogleFormInfo(**response.get("info"))
            response["responserUriId"] = response.get(
                "responderUri").rsplit("/e/", maxsplit=1)[1].rsplit("/")[0]
            items_list: list[dict[str, Any]] = response.get("items", [])
            items: list[GoogleFormItem] = []
            for item in items_list:
                if GOOGLE_FORM_ITEM_TYPE.PAGE_BREAK_ITEM in item.keys():
                    item["itemType"] = GOOGLE_FORM_ITEM_TYPE.PAGE_BREAK_ITEM
                elif GOOGLE_FORM_ITEM_TYPE.VIDEO_ITEM in item.keys():
                    item["itemType"] = GOOGLE_FORM_ITEM_TYPE.VIDEO_ITEM
                    item["itemData"] = item.get(
                        GOOGLE_FORM_ITEM_TYPE.VIDEO_ITEM)["video"]
                    uri: str = item["itemData"]["youtubeUri"]
                    item["itemData"]["videoId"] = uri.split("watch?v=")[-1]
                    item["itemData"]["caption"] = item.get(
                        GOOGLE_FORM_ITEM_TYPE.VIDEO_ITEM).get("caption")
                elif GOOGLE_FORM_ITEM_TYPE.IMAGE_ITEM in item.keys():
                    item["itemType"] = GOOGLE_FORM_ITEM_TYPE.IMAGE_ITEM
                    item["itemData"] = item.get(
                        GOOGLE_FORM_ITEM_TYPE.IMAGE_ITEM)["image"]
                elif GOOGLE_FORM_ITEM_TYPE.QUESTION_GROUP_ITEM in item.keys():
                    question_list: list[GoogleFormItem] = []
                    required: bool = False
                    for question_item in item.get("questionGroupItem").get("questions"):
                        question_item["itemId"] = question_item.get(
                            "questionId")
                        question_item["itemType"] = GOOGLE_FORM_ITEM_TYPE.QUESTION_ITEM
                        question_item.update(question_item.get("rowQuestion"))
                        item_data: dict[str, Any] = {}
                        item_data["questionId"] = question_item.get(
                            "questionId")
                        item_data["entryName"] = "entry." + \
                            str(int(question_item.get("questionId"), 16))
                        item_data["required"] = question_item.get(
                            "required", False)
                        item_data["questionType"] = GOOGLE_FORM_QUESTION_TYPE.CHOICE_QUESTION
                        columns: dict[str, Any] = item.get(
                            "questionGroupItem").get("grid").get("columns")
                        item_data["type"] = columns.get("type")
                        item_data["options"] = [option.get("value")
                                                for option in columns.get("options")]
                        question_item["itemData"] = item_data
                        question_list.append(GoogleFormItem(**question_item))
                        if not required:
                            required = item_data["required"]

                    item["itemType"] = GOOGLE_FORM_ITEM_TYPE.QUESTION_GROUP_ITEM
                    item["questions"] = question_list
                    item["itemData"] = item.get(
                        "questionGroupItem").get("grid")
                    item["itemData"]["required"] = required
                elif GOOGLE_FORM_ITEM_TYPE.QUESTION_ITEM in item.keys():
                    item["itemType"] = GOOGLE_FORM_ITEM_TYPE.QUESTION_ITEM
                    question_item: dict[str, Any] = item.get(
                        "questionItem").get("question")
                    item_data: dict[str, Any] = {}
                    item_data["questionId"] = question_item.get("questionId")
                    item_data["entryName"] = "entry." + \
                        str(int(question_item.get("questionId"), 16))
                    item_data["required"] = question_item.get(
                        "required", False)
                    if GOOGLE_FORM_QUESTION_TYPE.TEXT_QUESTION in question_item.keys():
                        item_data["questionType"] = GOOGLE_FORM_QUESTION_TYPE.TEXT_QUESTION
                        item_data["paragraph"] = question_item.get(
                            GOOGLE_FORM_QUESTION_TYPE.TEXT_QUESTION).get("paragraph", False)
                    elif GOOGLE_FORM_QUESTION_TYPE.CHOICE_QUESTION in question_item.keys():
                        item_data.update(question_item.get(
                            GOOGLE_FORM_QUESTION_TYPE.CHOICE_QUESTION))
                        item_data["questionType"] = GOOGLE_FORM_QUESTION_TYPE.CHOICE_QUESTION
                        item_data["options"] = [option.get(
                            "value") for option in item_data.get("options")]
                    elif GOOGLE_FORM_QUESTION_TYPE.SCALE_QUESTION in question_item.keys():
                        item_data.update(question_item.get(
                            GOOGLE_FORM_QUESTION_TYPE.SCALE_QUESTION))
                        item_data["questionType"] = GOOGLE_FORM_QUESTION_TYPE.SCALE_QUESTION
                    elif GOOGLE_FORM_QUESTION_TYPE.DATE_QUESTION in question_item.keys():
                        item_data.update(question_item.get(
                            GOOGLE_FORM_QUESTION_TYPE.DATE_QUESTION))
                        item_data["questionType"] = GOOGLE_FORM_QUESTION_TYPE.DATE_QUESTION
                    elif GOOGLE_FORM_QUESTION_TYPE.TIME_QUESTION in question_item.keys():
                        item_data.update(question_item.get(
                            GOOGLE_FORM_QUESTION_TYPE.TIME_QUESTION))
                        item_data["questionType"] = GOOGLE_FORM_QUESTION_TYPE.TIME_QUESTION
                    # elif GOOGLE_FORM_QUESTION_TYPE.FILE_UPLOAD_QUESTION in question_item.keys():
                    #     item_data.update(question_item.get(
                    #         GOOGLE_FORM_QUESTION_TYPE.FILE_UPLOAD_QUESTION))
                    #     item_data["questionType"] = GOOGLE_FORM_QUESTION_TYPE.FILE_UPLOAD_QUESTION
                    else:
                        raise NotImplementedError(
                            "Unknown Google Form Question Type. Data: " + json.dumps(item))

                    item["itemData"] = item_data
                else:
                    raise NotImplementedError(
                        "Unknown Google Form Item. Data: " + json.dumps(item))

                items.append(GoogleFormItem(**item))

            response["items"] = items
            return GoogleForm(**response)

        def _mapFormResponse(self, response: dict[str, Any], questions_order=None) -> FormResponse:
            date_format: str = "%Y-%m-%dT%H:%M:%S.%fZ"
            response["createTime"] = datetime.strptime(
                response.get("createTime"), date_format)
            response["lastSubmittedTime"] = datetime.strptime(
                response.get("lastSubmittedTime"), date_format)

            answers: list[FormAnswer] = []
            response_answers: dict[str, dict[str, Any]
                                   ] = response.get("answers")

            if response_answers is None:
                response["answers"] = answers
                return FormResponse(**response)

            for v in response_answers.values():
                textAnswers: dict[str, list[dict[str, str]]
                                  ] = v.get("textAnswers")
                textAnswer: str = ""
                if textAnswers:
                    for answer in textAnswers.get("answers"):
                        textAnswer += answer.get("value", "") + ", "
                    textAnswer = textAnswer[:-2]
                answers.append(FormAnswer(v.get("questionId"), textAnswer))

            if questions_order:
                questions_answered: list[str] = [
                    answer.questionId for answer in answers]
                for questionId in questions_order:
                    if questionId not in questions_answered:
                        answers.append(FormAnswer(questionId, ""))

            if questions_order:
                last_index: int = len(questions_order)
                answers = sorted(
                    answers,
                    key=lambda x: questions_order.index(
                        x.questionId) if x.questionId in questions_order else last_index)
                response["answers"] = list(
                    filter(lambda answer: answer.questionId in questions_order, answers))
            else:
                response["answers"] = answers

            return FormResponse(**response)
