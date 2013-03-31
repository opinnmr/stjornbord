from django.forms import ValidationError
from stjornbord.user.forms import validate_username

import datetime

def slugify(name):
    import unicodedata as ud
    import string
    
    name = unicode(name)

    slug = u''.join(c for c in ud.normalize('NFD', name.lower()) if ud.combining(c) == 0)
    slug = slug.replace(u'\xfe', "th")
    slug = slug.replace(u'\xe6', "ae")
    slug = slug.replace(u'\xf0', "d")

    allowed = string.ascii_lowercase + " " + string.digits
    return u''.join(c for c in slug if c in allowed)


def suggest_usernames(first_name, last_name, kennitala):
    """
    Suggest usernames based on the students name.
    
    F = Given name
    M1,M2,.. = Middle name(s)
    S = Surname

    Lower case = initial    
    """
    names = slugify("%s %s" % (first_name, last_name)).split(" ")

    f_name, m_name, s_name = names[0], names[1:-1], names[-1]
    f_init, m_init, s_init = f_name[0], ''.join([c[0] for c in m_name]), s_name[0]

    suggestions = []
    def add_suggestion(username):
        # Append last two digits of the year to username suggestion. This
        # is to make it easier to maintain unique usernames
        username = "%s%s" % (username, datetime.date.today().strftime("%y"))
        
        if username not in suggestions:
            try:
                # See if this is a valid username
                validate_username(username)
            except ValidationError:
                # Username invalid
                pass
            else:
                # Username valid, append to suggestion list
                suggestions.append(username)

    # F
    add_suggestion( f_name )

    # FS
    add_suggestion( f_name + s_name )

    # Fm, Fs, Fms
    add_suggestion( f_name + m_init )
    add_suggestion( f_name + m_init + s_init )
    add_suggestion( f_name + s_init )

    # FmS
    add_suggestion( f_name + m_init + s_name )

    # fms
    add_suggestion( f_init + m_init + s_init )

    # FM
    for n in m_name:
        add_suggestion( f_name + n )

    # MS
    for n in m_name:
        add_suggestion( n + s_name )

    # S
    add_suggestion( s_name )

    return suggestions
