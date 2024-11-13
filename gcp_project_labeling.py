import csv, argparse, sys

from googleapiclient import discovery
from oauth2client.client import GoogleCredentials


def arguments():

    parser = argparse.ArgumentParser(description="GCP projects labels updater")

    parser.add_argument(
        "--source_file",
        dest="source_file",
        required=True,
        help="Path to CSV file with labels and project id",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Shows output without generate any changes",
    )

    return parser.parse_args()


def aunthenticate():
    credentials = GoogleCredentials.get_application_default()

    return credentials


def get_project_number(project_id, credentials):
    service = discovery.build("cloudresourcemanager", "v1", credentials=credentials)
    response = service.projects().get(projectId=project_id).execute()

    return "projects/" + response["projectNumber"]


def patch_project_by_labels(project_number, credentials, labels, dry_run):
    if dry_run:
        print(
            "This action will add labels {} for this project {}".format(
                labels, project_number
            )
        )
    else:
        service = discovery.build("cloudresourcemanager", "v3", credentials=credentials)
        response = service.projects().patch(name=project_number, body=labels).execute()


def main():

    args = arguments()

    credentials = aunthenticate()

    with open(args.source_file, newline="") as csvfile:
        reader = csv.DictReader(csvfile, delimiter=",")
        for row in reader:
            try:
                labels = {"labels": {}}
                project_id = ""
                for header in reader.fieldnames:
                    if "finops" in header:
                        labels["labels"][header] = row[header]
                        if "finops_account-id" in header:
                            project_id = row[header]
                patch_project_by_labels(
                    project_number=get_project_number(project_id, credentials),
                    credentials=credentials,
                    labels=labels,
                    dry_run=args.dry_run,
                )

                # Prints the project id to an output file if tagging was successful
                sys.stdout = open("output.txt", "a")
                print(row["finops_account-id"])
                sys.stdout.close()

            except:
                # Prints the project id to an error file when tagging was unsuccessful
                sys.stdout = open("error.txt", "a")
                print(row["finops_account-id"] + " could not be tagged.")
                sys.stdout.close()


if __name__ == "__main__":
    main()
