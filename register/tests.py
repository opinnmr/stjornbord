#coding: utf8
import datetime
import django.test
from stjornbord.register.registration import suggest_usernames
from stjornbord.user.models import ReserverdUsername

"""
    def testReservedUsername(self):
        reserved_username = m.ReserverdUsername.objects.all()[0].username

        with self.assertRaises(ValidationError):
            self._create_user(reserved_username, self.OU_1)
"""

class UsernameSuggestionTestCase(django.test.TestCase):
    YEAR = datetime.date.today().strftime("%y")

    def testSuggestionsTwoNames(self):
        suggestions = suggest_usernames(u"Þorgerður", u"Ægisdóttir")

        # Remove expected suggestions
        suggestions.remove("thorgerdur%s" % self.YEAR)
        suggestions.remove("thorgerdura%s" % self.YEAR)
        suggestions.remove("aegisdottir%s" % self.YEAR)
        suggestions.remove("thorgerduraegisdottir%s" % self.YEAR)
        suggestions.remove("ta%s" % self.YEAR)

        # Verify that there are no unexpected suggestions
        self.assertEqual(suggestions, [])

    def testSuggestionsThreeNames(self):
        suggestions = suggest_usernames(u"Jóhann", u"Óli Guðmundsson")

        # Remove expected suggestions
        suggestions.remove("johann%s" % self.YEAR)
        suggestions.remove("johanno%s" % self.YEAR)
        suggestions.remove("johanng%s" % self.YEAR)
        suggestions.remove("johannog%s" % self.YEAR)
        suggestions.remove("oligudmundsson%s" % self.YEAR)
        suggestions.remove("johanngudmundsson%s" % self.YEAR)
        suggestions.remove("johannogudmundsson%s" % self.YEAR)
        suggestions.remove("gudmundsson%s" % self.YEAR)
        suggestions.remove("jog%s" % self.YEAR)
        suggestions.remove("johannoli%s" % self.YEAR)

        # Verify that there are no unexpected suggestions
        self.assertEqual(suggestions, [])

    def testSuggestionsFourNames(self):
        suggestions = suggest_usernames(u"Martin", u"Jónas Björn Swift")

        # Remove expected suggestions
        suggestions.remove("martin%s" % self.YEAR)
        suggestions.remove("martinswift%s" % self.YEAR)
        suggestions.remove("martinjbswift%s" % self.YEAR)
        suggestions.remove("martinbjorn%s" % self.YEAR)
        suggestions.remove("martinjonas%s" % self.YEAR)
        suggestions.remove("martinjb%s" % self.YEAR)
        suggestions.remove("martinjbs%s" % self.YEAR)
        suggestions.remove("martins%s" % self.YEAR)
        suggestions.remove("jonasswift%s" % self.YEAR)
        suggestions.remove("bjornswift%s" % self.YEAR)
        suggestions.remove("swift%s" % self.YEAR)
        suggestions.remove("mjbs%s" % self.YEAR)

        # Verify that there are no unexpected suggestions
        self.assertEqual(suggestions, [])

    def testSuggestionInUse(self):
        fname = u"Guðfríður"
        lname = u"Ýr Kvaran"
        suggestions1 = set(suggest_usernames(fname, lname))
        username = suggestions1.pop()

        ReserverdUsername.objects.create(username=username)

        suggestions2 = set(suggest_usernames(fname, lname))

        self.assertEqual(suggestions1, suggestions2)

