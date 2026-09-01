import json
import os
import urllib.request
import urllib.error

USERNAME = "MS04Monica"

GRAPHQL_URL = "https://api.github.com/graphql"

QUERY = """
query($username: String!) {
  user(login: $username) {
    contributionsCollection {
      contributionCalendar {
        totalContributions
        weeks {
          contributionDays {
            contributionCount
            date
            weekday
          }
        }
      }
    }
  }
}
"""


def fetch_contributions():
    token = os.environ.get("GH_PAT")

    if not token:
        raise RuntimeError(
            "GH_PAT environment variable is missing."
        )

    payload = json.dumps({
        "query": QUERY,
        "variables": {
            "username": USERNAME
        }
    }).encode("utf-8")

    request = urllib.request.Request(
        GRAPHQL_URL,
        data=payload,
        method="POST"
    )

    request.add_header(
        "Authorization",
        f"Bearer {token}"
    )

    request.add_header(
        "Content-Type",
        "application/json"
    )

    request.add_header(
        "Accept",
        "application/json"
    )

    try:
        with urllib.request.urlopen(request) as response:
            result = json.loads(
                response.read().decode("utf-8")
            )

    except urllib.error.HTTPError as error:
        print(
            "GitHub API error:",
            error.code,
            error.read().decode("utf-8")
        )
        raise

    if "errors" in result:
        raise RuntimeError(
            json.dumps(
                result["errors"],
                indent=2
            )
        )

    user = result["data"]["user"]

    if user is None:
        raise RuntimeError(
            f"GitHub user '{USERNAME}' was not found."
        )

    calendar = user[
        "contributionsCollection"
    ]["contributionCalendar"]

    output = {
        "username": USERNAME,
        "totalContributions": calendar[
            "totalContributions"
        ],
        "weeks": calendar["weeks"]
    }

    output_path = os.path.join(
        "assets",
        "pacman",
        "contributions.json"
    )

    os.makedirs(
        os.path.dirname(output_path),
        exist_ok=True
    )

    with open(
        output_path,
        "w",
        encoding="utf-8"
    ) as file:
        json.dump(
            output,
            file,
            indent=2
        )

    print()
    print("===================================")
    print(" GITHUB CONTRIBUTION DATA")
    print("===================================")
    print()
    print(f"User: {USERNAME}")
    print(
        f"Total contributions: "
        f"{output['totalContributions']}"
    )
    print(
        f"Weeks received: "
        f"{len(output['weeks'])}"
    )
    print()
    print(
        f"Created: {output_path}"
    )
    print()


if __name__ == "__main__":
    fetch_contributions()