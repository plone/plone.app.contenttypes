*** Settings ***

Library  Selenium2Library  timeout=120  implicit_wait=0.1

Resource  plone/app/contenttypes/tests/robot/keywords.txt
Variables  plone/app/testing/interfaces.py
Variables  plone/app/contenttypes/tests/robot/variables.py

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


*** Keywords ***

a folder '${folder-id}' with a document '${document-title}'
    Go to  ${TEST_FOLDER}/++add++Folder
    Input text  name=form.widgets.IDublinCore.title  ${folder-id}
    Click Button  Save
    Go to  ${TEST_FOLDER}/${folder-id}/++add++Document
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
