*** Settings ***

Library  Selenium2Library  timeout=2  implicit_wait=0

Resource  contenttypes_keywords.txt
Resource  library-settings.txt

Variables  plone/app/testing/interfaces.py

Suite Setup  Suite Setup
Suite Teardown  Suite Teardown

*** Variables ***

${front-page}  http://localhost:55001/plone/
${test-folder}  http://localhost:55001/plone/acceptance-test-folder

${PORT} =  55001
${ZOPE_URL} =  http://localhost:${PORT}
${PLONE_URL} =  ${ZOPE_URL}/plone
${BROWSER} =  Firefox


*** Test Cases ***

Test Folderlisting with all Contenttypes
    Log in as site owner
    Go to  ${test-folder}
    Create Folder  Test-Folder
    Create Image  Test-Image
    Create Collection  Test-Collection
    Create Event  Test-Event 
    Create Link  Test-Link 
    Create News Item  Test-News 
    Create Document  Test-Document

    Go to  ${test-folder}/folder_contents


    Page Should Contain  Test-Folder 
    Page Should Contain  Test-Image 
    Page Should Contain  Test-Collection 
    Page Should Contain  Test-Event 
    Page Should Contain  Test-Link 
    Page Should Contain  Test-News 
    Page Should Contain  Test-Document 
