import csv
from typing import Callable

from django.core.management.base import BaseCommand
from django.db import models

import api.consts as consts
from advertisement.models import (
    Advertisement,
    AdvertisementCategory,
    City,
    Region,
)
from users.models import User

BASE_PATH = "api/fixtures/"


class Command(BaseCommand):
    """Command to create test data."""

    def handle(self, *args, **options):
        """
        Main function to create test data.
        Checks if test data needs to be created and
        calls the appropriate data loading methods.
        """

        is_not_test_data_already_created = (
            len(Advertisement.objects.all())
            < consts.Message.MIN_COUNT_ADVERTISEMENT_IN_DB.value
        )

        if is_not_test_data_already_created:
            self.stdout.write(self.style.WARNING("Creating test data..."))

            for model in (
                User,
                Region,
                City,
                AdvertisementCategory,
                Advertisement,
            ):
                self.strategy(model)

            self.stdout.write(
                self.style.SUCCESS("Test data successfully created")
            )

        else:
            self.stdout.write(
                self.style.SUCCESS("Test data already exists, skipping...")
            )

    def strategy(self, model: models.Model) -> Callable:
        """Strategy to choose data loading method for each model."""

        strategy_dict = {
            User: (self.load_data_from_any_csv, f"{BASE_PATH}user.csv"),
            Region: (self.load_data_from_any_csv, f"{BASE_PATH}region.csv"),
            City: (self.load_data_from_city_csv, f"{BASE_PATH}city.csv"),
            AdvertisementCategory: (
                self.load_data_from_advertisement_category_csv,
                f"{BASE_PATH}advertisement_category.csv",
            ),
            Advertisement: (
                self.load_data_from_advertisement_csv,
                f"{BASE_PATH}advertisement.csv",
            ),
        }

        method = strategy_dict[model][0]

        try:
            return method(strategy_dict[model][1], model)

        except FileNotFoundError:
            self.stdout.write(
                self.style.ERROR(
                    f"CSV file {strategy_dict[model][1]} not found."
                )
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(
                    f"An error occurred while loading data from CSV file: {e}"
                )
            )

    @staticmethod
    def load_data_from_any_csv(csv_file_path, model_class):
        """Load data from CSV file into any model."""

        with open(csv_file_path, "r") as f:
            reader = csv.DictReader(f)

            for row in reader:
                model_class.objects.create(**row)

    @staticmethod
    def load_data_from_city_csv(csv_file_path, model_class):
        """Load data from CSV file into City model."""

        with open(csv_file_path, "r") as f:
            reader = csv.DictReader(f)

            for row in reader:
                region_id = int(row.pop("region"))
                region = Region.objects.get(pk=region_id)
                model_class.objects.create(region=region, **row)

    @staticmethod
    def load_data_from_advertisement_csv(csv_file_path, model_class):
        """Load data from CSV file into Advertisement model."""

        with open(csv_file_path, "r") as f:
            reader = csv.DictReader(f)

            for row in reader:
                model_class.objects.create(
                    user=User.objects.get(id=row.pop("user")),
                    city=City.objects.get(id=row.pop("city")),
                    category=AdvertisementCategory.objects.get(
                        id=row.pop("category")
                    ),
                    **row,
                )

    @staticmethod
    def load_data_from_advertisement_category_csv(csv_file_path, model_class):
        """Load data from CSV file into AdvertisementCategory model."""

        with open(csv_file_path, "r") as f:
            reader = csv.DictReader(f)

            for row in reader:
                parent_category_id = int(row.pop("parent_category"))

                if parent_category_id != 0:
                    parent_category = AdvertisementCategory.objects.get(
                        id=parent_category_id
                    )

                else:
                    parent_category = None
                model_class.objects.create(
                    parent_category=parent_category, **row
                )
