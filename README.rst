=========================
ButFriendly's PageObjects
=========================

ButFriendly's PageObjects are an implementation of the PageObject-pattern, which acts
as a facade to simplify the handling of the mostly complex structure and functionality
of HTML pages within Selenium-tests.

BFPO in detail
==============

The center of <> builds a product with its instances which are the subjects of our
test-efforts.

For each of our products we create an YAML-configuration, which contains all information
about our available instances, local and remote browsers as well as selenium itself.

A minimal setup must at least define a C{Product} and a C{PageObject}

    USE_SETTINGS=config.xml python tralala.py

A product would be an web-application for example, which can be run as multiple instances
with different configurations.

Quickstart
==========

Selenium
========

ChromeDriver needed: https://code.google.com/p/selenium/wiki/ChromeDriver

Start a hub
-----------

Env:

    VERSION=2.39.0
    SELENIUM_JAR="selenium-server-standalone-${VERSION}.jar"

Start selenium-hub:

    $ java -jar "${SELENIUM_JAR}" -role hub

The selenium-hub console will be available at
http://<hub_host>:4444/grid/console afterwards.

Start a node
------------

Start selenium-node:

    $ java -jar "${SELENIUM_JAR}" -role node -hub http://localhost:4444/grid/register \
        -browser browserName=firefox,platform=MAC,maxInstances=5

    $ java -jar "${SELENIUM_JAR}" -role node -hub http://localhost:4444/grid/register \
        -nodeConfig mac_node.conf

Run tests
=========

You can run tests with:

    $ python setup.py test

By default the tests generate a test.log in the current directory.