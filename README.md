# Stjórnborð Menntaskólans í Reykjavík

This package contains the user and network management portal for Menntaskólinn í Reykjavík (Reykjavik Junior Collage). The documentation is currently all in Icelandic, but feel free to snoop around and contact us if you are interested in the project! Our email is opinn you-know-what mr.is.

Í þessu skjali má finna leiðbeiningar til að sækja og setja upp þróunarumhverfi fyrir Stjórnborð MR. Stjórnborðið heldur utan um starfsmenn og nemendur og er notað við notenda- og tækjaumsjón. Stjórnborðið sér um að senda tilkynningar á fyrrverandi starfsmenn/nemendur og stýra lokunum á notendum, en gerir sjálft ekki breytingar á notendagrunnum. Til þess notum við litla þjóna sem spyrja Stjórnborðið reglulega um hvað eigi að gera. Einn þeirra, [Notendauppfærsluþjónninn](https://github.com/opinnmr/stjornbord-user-daemon) er kominn á GitHub, aðrir eru væntanlegir einhvern daginn.

# Formáli uppsetningar

Stjórnborðið er skrifað í Python og byggir á [Django](http://www.djangoproject.com). Hér fyrir neðan má finna uppsetningarleiðbeiningar, en við vekjum athygli á því að uppsetningu hefur verið skipt í tvennt: a) almenna uppsetningu og b) uppsetningu með Single-Sign-On stuðningi. Við mælum með því að byrjað sé á almennu uppsetningunni, þar sem SSO uppsetningin er nokkru flóknari, og einungis nauðsynleg ef samþætta á Stjórnborðið og Google Apps. Þessar leiðbeiningar einblína í raun aðallega á grunnuppsetningu, einungis er lauslega minnst á SSO uppsetningu í lokin.


# Uppsetning

Við notumst við sýndarumhverfi ([virtual environment](http://pypi.python.org/pypi/virtualenv)) fyrir Stjórnborðið þar sem það leyfir okkur að setja upp pakka sem Stjórnborðið styðst við án þess að það hafi áhrif á annað í tölvunni - og öfugt. Fyrst þarf því að sækja `virtualenv` og `pip` pakkana sem seinna aðstoða okkur við að setja upp umhverfið.

## Forkröfur: Ubuntu Linux

    casanova:~$ sudo apt-get install python-pip python-virtualenv git

## Forkröfur: Mac OS X

### Leið 1: Nota Python sem fylgir OS X

Hægt er að nota Python sem fylgir OS X, en sækja þarf [Command Line Tools for Xcode](http://developer.apple.com/downloads).

    $ sudo easy_install virtualenv
    $ sudo easy_install pip

### Leið 2: Nota MacPorts

Ef þú notar [MacPorts](http://www.macports.org/) og vilt heldur nota Python útgáfu sem þú hefur sett upp á þann veg, getur þú notað eitthvað í líkingu við (mv. Python 2.7)

    $ sudo port install py27-virtualenv py27-pip


## Uppsetning þróunarumhverfis

Búum til sýnarumhverfi fyrir Stjórnborðið:

    casanova:~$ virtualenv --no-site-packages mr-test
    New python executable in mr-test/bin/python
    Installing distribute.....done.
    Installing pip...done.

Förum inn í sýndarumhverfið og virkjum það. Við það breytist command prompt línan.

    casanova:~$ cd mr-test/
    casanova:~/mr-test$ source bin/activate
    
    (mr-test)casanova:~/mr-test$

Sækjum Stjórnborðið:

    (mr-test)casanova:~/mr-test$ git clone git://github.com/opinnmr/stjornbord.git

Þetta sækir nýjustu útgáfu af Stjórnborðinu og setur hana í möppuna `stjornbord`. Ásamt kóðanum er sótt skráin `requirements.txt`, en hana er hægt að nota til að setja upp pakka sem Stjórnborðið styðst við.

    (mr-test)casanova:~/mr-test$ pip install -r stjornbord/requirements.txt

Nú er uppsetningu lokið og næst er að ræsa Stjórnborðið (sjá neðar).


## Uppsetning keyrsluumhverfis

MR keyrir Stjórnborðið í gegnum Apache/mod_wsgi. Einn daginn setjum við inn leiðbeiningar um hvernig megi setja það upp.


# Ræsa Stjórnborðið

Við gerum ráð fyrir því að allar skipanir hér fyrir neðan séu keyrar innan úr sýndarumhverfinu. Þú sérð hvort sýndarumhverfið sé virkt á command prompt línunni þinni, ef hún byrjar á nafni umhverfisins í sviga, að þá ertu á réttri leið.

Ef þú ert ekki inni í sýndarumhverfinu getur þú alltaf komist inn í það með því að túlka bin/activate skjalið:

    casanova:~$ cd mr-test/
    casanova:~/mr-test$ source bin/activate
    (mr-test)casanova:~/mr-test$ 


## Fyrsta skipti

Í fyrsta skipti sem Stjórnborðið er ræst þarf að búa til gagnagrunn. Django hjálpar okkur við það. Þegar við keyrum eftirfarandi skipun erum við spurð hvort stofna eigi superuser. Við svörum því játandi og fylgjum leiðbeiningum á skjá til að stofna ofur notanda.

    (mr-test)casanova:~/mr-test$ cd stjornbord/
    (mr-test)casanova:~/mr-test/stjornbord$ python manage.py syncdb

Eftir þetta hefur SQLite gagnagrunnurinn okkar verið búinn til. Hann ætti að vera í skrá sem heitir `stjornbord.sdb`. Hann mun innihalda grunnupplýsingar til að hægt sé að nota kerfið.

Ef þú vilt örlitlar auka upplýsingar (dæmi um starfsmann og tæki) getur þú hlaðið inn demo gögnum, en þetta er valfrjálst:

    (mr-test)casanova:~/mr-test/stjornbord$ python manage.py loaddata */fixtures/demo_data.json


## Ræsa vefviðmót

Til að ræsa vefviðmót Stjórnborðsins keyrum við eftirfarandi skipun (pössum að vera í sýndarumhverfinu):

    (mr-test)casanova:~/mr-test/stjornbord$ python manage.py runserver
    Validating models...
    0 errors found

    Django version 1.2.7, using settings 'stjornbord.settings'
    Development server is running at http://127.0.0.1:8000/
    Quit the server with CONTROL-C.


Nú ættir þú að geta beint vafranum þínum á [http://127.0.0.1:8000/](http://127.0.0.1:8000/) og skráð þig inn í Stjórnborðið!


# Uppfærsla notenda

Líkt og drepið var á í innganginum, þá sér Stjórnborðið sjálft ekki um að uppfæra notendagrunninn. Til þess notum við litla þjóna sem spyrja Stjórnborðið reglulega um hvað eigi að gera. Þessir þjónar eru væntanlegir á GitHub á næstunni!

# Single-Sign-On stuðningur

Stuttlega: til að virkja Single-Sign-On stuðning þarf að:

* Setja upp `python-libxml2` og `xmlsec`. Það er best gert gegnum `apt-get`, `yum`, MacPorts, Homebrew eða einhverskonar pakkakerfi.
* Keyra `requirements-sso.txt` í gegnum pip (muna að vera inni í virtualenv). Inni í þessari skrá eru einnig leiðbeiningar um hvernig vísa má libxml2 í global site-packages.
* Búa til public/private lykla og vista þá í ssokeys möppuna sem `rsacert.pem`, `rsaprivkey.pem` og `rsapubkey.pem`.
* Setja `GOOGLE_SSO_ENABLE = True` í `settings_dev.py`


# Villur og vesen

Ef þú rekst á villur, lendir í vandræðum eða hefur einhverjar ábendingar væri gaman að heyra frá þér! Hópurinn sem stendur á bakvið Opinn MR hefur netfangið opinn hjá mr.is.

Takk!
Björn Patrick Swift <bjorn@swift.is>
