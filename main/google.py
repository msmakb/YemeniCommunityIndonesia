"""
* This is a module for interacting with the Google Drive API. 
* 
* It allows you to authenticate with your Google Drive account, 
* and perform various actions such as creating and retrieving files and folders.
* 
* Please note that this module is not complete and may require additional functionality and error handling.
* 
* Created by: Mohammed Ba Karman
* E-Mail: msmabk11@gmail.com
* Version: 1.0.0
"""
import json
from pathlib import Path
from dataclasses import dataclass
from collections import namedtuple
from typing import Any, Final, Optional, Union
from os.path import isfile as isFileLocallyExist

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
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
    'VIDEO'
])(
    'application/vnd.google-apps.audio',
    'application/vnd.google-apps.document',
    'application/vnd.google-apps.file',
    'application/vnd.google-apps.folder',
    'application/vnd.google-apps.photo',
    'application/vnd.google-apps.presentation',
    'application/vnd.google-apps.spreadsheet',
    'application/vnd.google-apps.unknown',
    'application/vnd.google-apps.video'
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


@dataclass
class FileResources:
    id: str
    name: str
    kind: str = None
    mimeType: str = None
    starred: bool = False

    def __str__(self) -> str:
        main_str_presentation = f"ID: {self.id} | File Name: {self.name}"
        if self.kind:
            main_str_presentation += f" | kind: {self.kind}"
        if self.mimeType:
            main_str_presentation += f" | Mime Type: {self.mimeType}"
        if self.starred:
            main_str_presentation += f" | Starred: {self.starred}"
        return main_str_presentation


class GoogleAuthenticationError(Exception):
    pass


class GoogleDriveService:

    API_NAME = 'drive'
    API_VERSION = 'v3'
    SCOPES: Final[list[str]] = [
        'https://www.googleapis.com/auth/drive'
    ]

    def __init__(self) -> None:
        self.credentials = None
        self._driveService = None

    def __enter__(self):
        return self

    def __exit__(self, *args, **kwargs):
        if self._driveService:
            self._driveService.close()

    def authenticate(self, auth_file_path: str):
        authenticationError: GoogleAuthenticationError = None

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

        self._driveService: Resource = build(
            self.API_NAME, self.API_VERSION, credentials=self.credentials)

    def _isAuthenticated(self):
        if not self.credentials:
            raise GoogleAuthenticationError(
                "Please authenticate before using the file service.")

    def about(self):
        self._isAuthenticated()
        about: Resource = self._driveService.about()
        return self._About(about)

    def fileService(self):
        self._isAuthenticated()
        fileService: Resource = self._driveService.files()
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
            except:
                return None

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

            response: dict[str, Any] = self.fileService.list(
                **metadata).execute()

            file_list: list[FileResources] = []
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
