*** Settings ***

Resource  plone/app/robotframework/keywords.robot
Resource  plone/app/contenttypes/tests/robot/keywords.txt

Variables  plone/app/contenttypes/tests/robot/variables.py

Test Setup  Run keywords  Setup Testcontent  Open test browser
Test Teardown  Close all browsers

*** Variables ***

*** Test cases ***

Scenario: Test listing views
    Given I am logged in as site owner

    When I Go to  ${PLONE_URL}/${TEST_FOLDER_ID}/listing_view
    Then Listing should list contained content

    When I Go to  ${PLONE_URL}/${TEST_FOLDER_ID}/summary_view
    Then Listing should list contained content

    When I Go to  ${PLONE_URL}/${TEST_FOLDER_ID}/tabular_view
    Then Listing should list contained content

    When I Go to  ${PLONE_URL}/${TEST_FOLDER_ID}/full_view
    Then Listing should list contained content in detail

    When I Go to  ${PLONE_URL}/${TEST_FOLDER_ID}/test_album/album_view
    Then Album should list contained images and albums


    When I Go to  ${PLONE_URL}/${TEST_FOLDER_ID}/test_collection/listing_view
    Then Listing should list all content

    When I Go to  ${PLONE_URL}/${TEST_FOLDER_ID}/test_collection/summary_view
    Then Listing should list all content

    When I Go to  ${PLONE_URL}/${TEST_FOLDER_ID}/test_collection/tabular_view
    Then Listing should list all content

    When I Go to  ${PLONE_URL}/${TEST_FOLDER_ID}/test_collection/full_view
    Then Listing should list all content in detail

    When I Go to  ${PLONE_URL}/${TEST_FOLDER_ID}/test_collection/album_view
    Then Album should list all images and albums


*** Keywords ***

Listing should list contained content
  Page Should Contain  Test Document
  Page Should Contain  Test News Item
  Page Should Contain  Test Event
  Page Should Contain  Test Collection
  Page Should Contain  Test Link
  Page Should Contain  Test File
  Page Should Contain  Test Image
  Page Should Contain  Test Album
  Page Should Not Contain  Test Album Image 1
  Page Should Not Contain  Test Album Image 2
  Page Should Not Contain  Test Album Image 3
  Page Should Not Contain  Test Sub Album
  Page Should Not Contain  Test Sub Album Image 1
  Page Should Not Contain  Test Sub Album Image 2
  Page Should Not Contain  Test Sub Album Image 3

Listing should list contained content in detail
  Page Should Contain  Test Document
  Page Should Contain  this is a test document
  Page Should Contain  Test News Item
  Page Should Contain  this is a test news item
  Xpath Should Match X Times  //img[@title="Test News Item"]  0
  Page Should Contain  Test Event
  Page Should Contain  this is a test event
  Page Should Contain  Test Collection
  Page Should Contain  this is a test collection
  Page Should Contain  Test Link
  Page Should Contain  http://plone.org
  Page Should Contain  Test File
  Page Should Contain  file.pdf
  Page Should Contain  Test Image
  Xpath Should Match X Times  //img[@title="Test Image"]  1
  Page Should Contain  Test Album
  Page Should Contain  Test Album Image 1
  Xpath Should Match X Times  //img[@title="Test Album Image 1"]  0
  Page Should Contain  Test Album Image 2
  Xpath Should Match X Times  //img[@title="Test Album Image 2"]  0
  Page Should Contain  Test Album Image 3
  Xpath Should Match X Times  //img[@title="Test Album Image 3"]  0
  Page Should Contain  Test Sub Album
  Page Should Contain  Test Sub Album Image 1
  Xpath Should Match X Times  //img[@title="Test Sub Album Image 1"]  0
  Page Should Contain  Test Sub Album Image 2
  Xpath Should Match X Times  //img[@title="Test Sub Album Image 2"]  0
  Page Should Contain  Test Sub Album Image 3
  Xpath Should Match X Times  //img[@title="Test Sub Album Image 3"]  0

Album should list contained images and albums
  Page Should Contain  Test Album Image 1
  Xpath Should Match X Times  //img[@title="Test Album Image 1"]  1
  Page Should Contain  Test Album Image 2
  Xpath Should Match X Times  //img[@title="Test Album Image 2"]  1
  Page Should Contain  Test Album Image 3
  Xpath Should Match X Times  //img[@title="Test Album Image 3"]  1
  Page Should Contain  Test Sub Album


Listing should list all content
  Page Should Contain  Test Document
  Page Should Contain  Test News Item
  Page Should Contain  Test Event
  Page Should Contain  Test Collection
  Page Should Contain  Test Link
  Page Should Contain  Test File
  Page Should Contain  Test Image
  Page Should Contain  Test Album
  Page Should Contain  Test Album Image 1
  Page Should Contain  Test Album Image 2
  Page Should Contain  Test Album Image 3
  Page Should Contain  Test Sub Album
  Page Should Contain  Test Sub Album Image 1
  Page Should Contain  Test Sub Album Image 2
  Page Should Contain  Test Sub Album Image 3

Listing should list all content in detail
  Page Should Contain  Test Document
  Page Should Contain  this is a test document
  Page Should Contain  Test News Item
  Page Should Contain  this is a test news item
  Xpath Should Match X Times  //img[@title="Test News Item"]  0
  Page Should Contain  Test Event
  Page Should Contain  this is a test event
  Page Should Contain  Test Collection
  Page Should Contain  this is a test collection
  Page Should Contain  Test Link
  Page Should Contain  http://plone.org
  Page Should Contain  Test File
  Page Should Contain  file.pdf
  Page Should Contain  Test Image
  Xpath Should Match X Times  //img[@title="Test Image"]  1
  Page Should Contain  Test Album
  Page Should Contain  Test Album Image 1
  Xpath Should Match X Times  //img[@title="Test Album Image 1"]  1
  Page Should Contain  Test Album Image 2
  Xpath Should Match X Times  //img[@title="Test Album Image 2"]  1
  Page Should Contain  Test Album Image 3
  Xpath Should Match X Times  //img[@title="Test Album Image 3"]  1
  Page Should Contain  Test Sub Album
  Page Should Contain  Test Sub Album Image 1
  Xpath Should Match X Times  //img[@title="Test Sub Album Image 1"]  1
  Page Should Contain  Test Sub Album Image 2
  Xpath Should Match X Times  //img[@title="Test Sub Album Image 2"]  1
  Page Should Contain  Test Sub Album Image 3
  Xpath Should Match X Times  //img[@title="Test Sub Album Image 3"]  1

Album should list all images and albums
  Page Should Contain  Test Image
  Xpath Should Match X Times  //img[@title="Test Image"]  2
  Page Should Contain  Test Album Image 1
  Xpath Should Match X Times  //div[@class="photoAlbumEntry" and not(@class="photoAlbumFolder")]//img[@title="Test Album Image 1"]  1
  Page Should Contain  Test Album Image 2
  Xpath Should Match X Times  //div[@class="photoAlbumEntry" and not(@class="photoAlbumFolder")]//img[@title="Test Album Image 2"]  1
  Page Should Contain  Test Album Image 3
  Xpath Should Match X Times  //div[@class="photoAlbumEntry" and not(@class="photoAlbumFolder")]//img[@title="Test Album Image 3"]  1
  Page Should Contain  Test Sub Album Image 1
  Xpath Should Match X Times  //div[@class="photoAlbumEntry" and not(@class="photoAlbumFolder")]//img[@title="Test Sub Album Image 1"]  1
  Page Should Contain  Test Sub Album Image 2
  Xpath Should Match X Times  //div[@class="photoAlbumEntry" and not(@class="photoAlbumFolder")]//img[@title="Test Sub Album Image 2"]  1
  Page Should Contain  Test Sub Album Image 3
  Xpath Should Match X Times  //div[@class="photoAlbumEntry" and not(@class="photoAlbumFolder")]//img[@title="Test Sub Album Image 3"]  1
  Page Should Contain  Test Album
  Page Should Contain  Test Sub Album



Setup Testcontent
  Given I am logged in as site owner
  Create Content  type=Document  container=${PLONE_PATH}/${TEST_FOLDER_ID}  id=test_document  title=Test Document  text=this is a test document
  Create Content  type=News Item  container=${PLONE_PATH}/${TEST_FOLDER_ID}  id=test_news_item  title=Test News Item  text=this is a test news item
  Create Content  type=Event  container=${PLONE_PATH}/${TEST_FOLDER_ID}  id=test_event  title=Test Event  text=this is a test event
  Create Content  type=Collection  container=${PLONE_PATH}/${TEST_FOLDER_ID}  id=test_collection  title=Test Collection  query=${COLLECTION_TEST_QUERY}  text=this is a test collection
  Create Content  type=Link  container=${PLONE_PATH}/${TEST_FOLDER_ID}  id=test_link  title=Test Link  remoteUrl=http://plone.org
  Create Content  type=File  container=${PLONE_PATH}/${TEST_FOLDER_ID}  id=test_file  title=Test File
  Create Content  type=Image  container=${PLONE_PATH}/${TEST_FOLDER_ID}  id=test_image  title=Test Image
  Create Content  type=Folder  container=${PLONE_PATH}/${TEST_FOLDER_ID}  id=test_album  title=Test Album
  Create Content  type=Image  container=${PLONE_PATH}/${TEST_FOLDER_ID}/test_album  id=album_image_1  title=Test Album Image 1
  Create Content  type=Image  container=${PLONE_PATH}/${TEST_FOLDER_ID}/test_album  id=album_image_2  title=Test Album Image 2
  Create Content  type=Image  container=${PLONE_PATH}/${TEST_FOLDER_ID}/test_album  id=album_image_3  title=Test Album Image 3
  Create Content  type=Folder  container=${PLONE_PATH}/${TEST_FOLDER_ID}/test_album  id=test_subalbum  title=Test Sub Album
  Create Content  type=Image  container=${PLONE_PATH}/${TEST_FOLDER_ID}/test_album/test_subalbum  id=subalbum_image_1  title=Test Sub Album Image 1
  Create Content  type=Image  container=${PLONE_PATH}/${TEST_FOLDER_ID}/test_album/test_subalbum  id=subalbum_image_2  title=Test Sub Album Image 2
  Create Content  type=Image  container=${PLONE_PATH}/${TEST_FOLDER_ID}/test_album/test_subalbum  id=subalbum_image_3  title=Test Sub Album Image 3

I go to
    [Arguments]  ${location}
    Go to  ${location}
