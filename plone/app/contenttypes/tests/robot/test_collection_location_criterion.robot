*** Settings ***

Variables  plone/app/testing/interfaces.py
Variables  plone/app/contenttypes/tests/robot/variables.py

Library  Selenium2Library  timeout=${SELENIUM_TIMEOUT}  implicit_wait=${SELENIUM_IMPLICIT_WAIT}

Resource  library-settings.txt
Resource  plone/app/contenttypes/tests/robot/keywords.txt

Suite Setup  Suite Setup
Suite Teardown  Suite Teardown


*** Test Cases ***

Scenario: Test Relative Location Criterion
    Given a document   Document outside Folder
      And a folder 'my-folder' with a document 'Document within Folder'
      And a collection  My Collection
     When I set the collection's relative location criterion to  ../my-folder
     Then the collection should contain  Document within Folder
      And the collection should not contain  Document outside Folder


Scenario: Test Absolute Location Criterion
    Given a document   Document outside Folder
      And a folder 'my-folder' with a document 'Document within Folder'
      And a collection  My Collection
     When I set the collection's absolute location criterion to  /robot-test-folder/my-folder/
     Then the collection should contain  Document within Folder
      And the collection should not contain  Document outside Folder


*** Keywords ***

a folder '${folder-id}' with a document '${document-title}'
    Go to  ${TEST_FOLDER}/++add++Folder
    Wait until page contains element  name=form.widgets.IDublinCore.title
    Input text  name=form.widgets.IDublinCore.title  ${folder-id}
    Click Button  Save
    Go to  ${TEST_FOLDER}/${folder-id}/++add++Document
    Wait until page contains element  name=form.widgets.IDublinCore.title
    Input text  name=form.widgets.IDublinCore.title  ${document-title}
    Click Button  Save

I set the collection's relative location criterion to
    [Arguments]  ${criterion}
    Click Link  Edit
    Wait Until Page Contains Element  xpath=//select[@name="addindex"]
    Select From List  xpath=//select[@name="addindex"]  Location
    Wait Until Page Contains Element  xpath=//select[@class='queryoperator']
    Select From List  xpath=//select[@class='queryoperator']  Relative path
    Input Text  xpath=//input[@name='form.widgets.query.v:records']  ${criterion}
    Click Button  Save

I set the collection's absolute location criterion to
    [Arguments]  ${criterion}
    Click Link  Edit
    Wait Until Page Contains Element  xpath=//select[@name="addindex"]
    Select From List  xpath=//select[@name="addindex"]  Location
    Wait Until Page Contains Element  xpath=//select[@class='queryoperator']
    Select From List  xpath=//select[@class='queryoperator']  Absolute path
    Input Text  xpath=//input[@name='form.widgets.query.v:records']  ${criterion}
    Click Button  Save
