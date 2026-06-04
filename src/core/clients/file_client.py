import os
from core.clients.http_client import HttpClient


class FileClient:

    def download_file(
        self,
        url,
        output_path
    ):

        os.makedirs(
            os.path.dirname(output_path),
            exist_ok=True
        )

        response = HttpClient.download(url, stream=True)

        with open(
            output_path,
            "wb"
        ) as file:

            for chunk in response.iter_content(
                chunk_size=8192
            ):

                file.write(chunk)

        return output_path
