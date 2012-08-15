# coding: utf-8

import os
import codecs
import datetime

from django.core.validators import email_re

from stjornbord.student.models import Student, Klass, LegalGuardian
from stjornbord.ou.models import Status
from stjornbord.user.models import UserStatus

FIELDS = ["Kennitala", "Nafn", "Bekkur", "Netfang forrm1", "Netfang forrm2"]
HEADER_TOKEN = "Kennitala"
DELIMITER = "\t"

class InnaParserException(Exception): pass

class InnaParser(object):
    def __init__(self, filename, pretend = True):
        self.filename = filename
        self.cache    = {}
        
        self.ACTIVE_STUDENT  = Status.objects.get(pk=1)
        self.FORMER_STUDENT  = Status.objects.get(pk=2)
        
        self.stats      = { 'create':0, 'update':0, 'delete':0 }
        self.pretend    = pretend
        

    def parse_inna(self):
        """
        Open up a given Inna student list and extract select information
        on students. Returns a list of student tuples with the fields
        listed in FIELDS
        """
        inna = codecs.open(self.filename, "r", "iso-8859-1")

        # Define the fields I am interested in extracting
        field_map   = dict.fromkeys(FIELDS)

        # Find the header line. This is typically line two or three, and we
        # assume it's the first one that includes the required "Kennitala"
        # (HEADER_TOKEN) field.
        available_fields = []
        for line in inna:
            if HEADER_TOKEN in line:
                available_fields = line.strip().split(DELIMITER)
                break

        # Run through my wanted field list and find it's index number.
        # NOTE: This makes the assumption that if there are two or more
        # fields with the same name, we want the first one.

        for field in FIELDS:
            try:
                field_map[field] = available_fields.index(field)
            except ValueError, e:
                raise InnaParserException("Could not find '%s' in list of fields" % field)

        # Scroll through the rest of the file extracting the fields we are
        # interested in. Create a new data structure only containing fields
        # of interest.
        students = []
        for line in inna:
            line = line.strip()
            if line:
                line = line.split(DELIMITER)
                student = []
                for field in FIELDS:
                    student.append(line[field_map[field]])
                students.append(student)

        inna.close()
    
        return students


    def find_student(self, kennitala, *args):
        """
        Look for student object based on kennitala. If the Student
        is found, remove from the original list
        """
        retval = None

        for student_list in args:
            for student in student_list:
                if student.kennitala == kennitala:
                    student_list.remove(student)
                    return student
        return None


    def get_object(self, model, name):
        """
        Find the requested Klass/Guardian/etc object in cache and return in
        """
        model_name = model.__name__

        if not model_name in self.cache:
            self.cache[model_name] = list(model.objects.all())
        
        for item in self.cache[model_name]:
            if unicode(item) == name:
                return item
        
        # Hmm, since we got to here the requested object doesn't
        # seem to exist. Oh, well. Let's create it and add it to
        # the cache
        new_item = model()
        
        if model_name == "Klass":
            new_item.name = name
        elif model_name == "LegalGuardian":
            new_item.email = name
        else:
            raise RuntimeError("Don't know how to make a new %s" % model_name)
        
        new_item.save()

        self.cache[model_name].append(new_item)
        return new_item

    def get_guardian_emails(self, *args):
        """
        Takes Inna guardian email fields and returns valid email addresses.
        """
        for guardian in args:
            # Some parents register two addresses
            emails = guardian.split(",")
            for email in emails:
                email = email.strip()
                if email and email_re.search(email):
                    yield email

    def update(self):
        # Get students from Inna file
        inna_students = self.parse_inna()

        # Get current student list from database and caching statuses
        active_students = list(Student.objects.filter(status__id=1))
        other_students  = list(Student.objects.filter(status__id__gt=1))

        # Iterate through the Inna students. Add new students and update
        # the others (names and klasses)
        for kennitala, name, klass, guardian1, guardian2 in inna_students:
            first_name, last_name = name.rsplit(" ", 1)

            student = self.find_student(kennitala, active_students, other_students)
            if not student:
                self.stats['create'] += 1
                student = Student(kennitala  = kennitala)
            else:
                self.stats['update'] += 1

            if self.pretend:
                continue

            student.status      = self.ACTIVE_STUDENT
            student.klass       = self.get_object(Klass, klass)
            student.first_name  = first_name
            student.last_name   = last_name
            student.save()
            
            student.guardians.clear()
            
            for guardian_email in self.get_guardian_emails(guardian1, guardian2, ):
                student.guardians.add(self.get_object(LegalGuardian, guardian_email))                

        # Now let's see if there are any students left in the self.ACTIVE_STUDENTs
        # list. If so, those need to be deactivated as they are no longer
        # active (according to Inna)
        for student in active_students:
            self.stats['delete'] += 1

            if not self.pretend:
                student.status = self.FORMER_STUDENT
                student.save()


if __name__ == '__main__':
    os.environ['DJANGO_SETTINGS_MODULE'] = 'stjornbord.settings'
    
