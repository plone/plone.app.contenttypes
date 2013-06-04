*** Settings ***
Suite Setup     Suite Setup
Suite Teardown  Suite Teardown
Variables       plone/app/testing/interfaces.py
Variables       plone/app/contenttypes/tests/robot/variables.py
Library         Selenium2Library  timeout=${SELENIUM_TIMEOUT}  implicit_wait=${SELENIUM_IMPLICIT_WAIT}
Resource        plone/app/contenttypes/tests/robot/keywords.txt
Variables       ../variables.py

*** Test Cases ***
Scenario: Test Migration
  Given a ATNewsItem  Test news item
  When I install plone.app.contenttypes
   And I migrate all content
  Then I can edit my news item

*** Keywords ***
I go to
  [Arguments]  ${location}
  Go to  ${location}

I install plone.app.contenttypes
  Go to  ${PLONE_URL}/prefs_install_products_form
  Select Checkbox  id=plone.app.contenttypes
  Click Button  Activate
  Sleep  10

I migrate all content
  Go to  ${PLONE_URL}/migrate_from_atct

I can edit my news item
  Go to  ${PLONE_URL}/test-news-item/edit
  Input text  name=form.widgets.IDublinCore.title  A new title
  fill in metadata
  Click Button  Save
  Wait until page contains  A new title
