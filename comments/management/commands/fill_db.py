from django.core.management.base import BaseCommand
from comments.libs.misc import generate_tree_of_comments


class Command(BaseCommand):

    def handle(self, *args, **options):

        self.stdout.write('***** Start generation! *****')

        generate_tree_of_comments()

        self.stdout.write('***** Successfully! *****')
