#!/usr/bin/env python

import sys
import csv
import json
import requests

from typing import TypedDict, TextIO


LOGIN_QUERY = """
mutation login($email: String!, $password: String!) {
  login(email: $email, password: $password) {
    token
    email
    languages
    profile {
      id
      handle
      name
      bio
      image
    }
  }
}
"""

RATINGS_QUERY = """
query myReviews($limit: Int!, $offset: Int!) {
  myReviews(limit: $limit, offset: $offset) {
    data {
      rating
      updatedAt
      text
      book {
        title
        authors {
          name
        }
      }
    }
  }
}
"""


class AuthorResponse(TypedDict):
    name: str


class BookResponse(TypedDict):
    title: str
    authors: list[AuthorResponse]


class RatingsResponse(TypedDict):
    book: BookResponse
    rating: float
    updatedAt: str
    text: str


class RatingsAPIResponse(TypedDict):
    data: RatingsResponse


class RatingsExport(TypedDict):
    title: str
    authors: list[str]
    rating: float
    updatedAt: str
    text: str


class LiteralException(Exception):
    pass


class LiteralExporter:
    URL = "https://literal.club/graphql/"

    def __init__(self, email: str, password: str, export_format: str = "csv"):
        self.email = email
        self.password = password
        self._session: requests.Session | None = None
        self.export_format = export_format

    @property
    def session(self) -> requests.Session:
        if not self._session:
            self._session = requests.Session()
            self._login()
        return self._session

    def _login(self):
        response = requests.post(
            self.URL,
            json={
                "query": LOGIN_QUERY,
                "variables": {"email": self.email, "password": self.password},
            },
        )

        try:
            login_response = response.json()
        except ValueError:
            raise LiteralException(str(response))

        if "errors" in login_response:
            errors = ", ".join(
                e.get("message") for e in login_response.get("errors", [])
            )
            raise LiteralException(f"Could not login: {errors}")

        self.session.headers[
            "Authorization"
        ] = f"Bearer {login_response['data']['login']['token']}"

    def fetch_ratings(self) -> list[RatingsExport]:
        """
        Fetch ratings for books.
        """
        data: list[RatingsExport] = []
        limit = 100
        offset = 0
        while True:
            ratings: list[RatingsAPIResponse] = self.session.post(
                self.URL,
                json={
                    "query": RATINGS_QUERY,
                    "variables": {"limit": limit, "offset": offset},
                },
            ).json()["data"]["myReviews"]
            for result in ratings:
                result_data = result["data"]
                data.append(
                    {
                        "title": result_data["book"]["title"],
                        "authors": [a["name"] for a in result_data["book"]["authors"]],
                        "rating": result_data["rating"],
                        "updatedAt": result_data["updatedAt"],
                        "text": result_data["text"],
                    }
                )
            if len(ratings) < limit:
                break
            offset += limit
        return data

    def export_ratings(
        self, export_file: TextIO = sys.stdout, export_format: str | None = None
    ):
        """
        Export ratings for books, writing them to export_file in the format specified.
        """
        data = self.fetch_ratings()
        export_format = export_format or self.export_format
        if self.export_format == "json":
            export_file.write(json.dumps(data))
        else:
            csv_writer = csv.writer(export_file)
            csv_writer.writerow(
                [
                    "Title",
                    "Author",
                    "Rating",
                    "Date",
                    "Comment",
                ]
            )
            for rating in data:
                csv_writer.writerow(
                    [
                        rating["title"],
                        ", ".join(a for a in rating["authors"]),
                        rating["rating"],
                        rating["updatedAt"],
                        rating["text"],
                    ]
                )


def main():
    import argparse
    from getpass import getpass

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--outfile",
        help="Output file to write to. If not provided, the data will be written to stdout.",
    )
    parser.add_argument("--email", "-e", help="Literal email address")
    parser.add_argument("--password", "-p", help="Literal password")
    parser.add_argument(
        "--format", "-f", help="Export format", choices=["csv", "json"], default="csv"
    )
    args = parser.parse_args()

    email = args.email
    password = args.password

    if not email:
        email = input("Enter the email address for your Literal account: ")
    if not password:
        password = getpass("Enter the password for your Literal account: ")

    try:
        exporter = LiteralExporter(email, password, export_format=args.format)
        if args.outfile:
            with open(args.outfile, "w") as f:
                exporter.export_ratings(f)
        else:
            exporter.export_ratings()
    except LiteralException as err:
        sys.stderr.write(f"{err}\n")
    except Exception as err:
        sys.stderr.write(f"Unhandled exception: {err}")


if __name__ == "__main__":
    main()
