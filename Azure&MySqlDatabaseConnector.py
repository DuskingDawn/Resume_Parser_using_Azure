import mysql.connector
from azure.core.credentials import AzureKeyCredential
from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.ai.formrecognizer._helpers import get_content_type
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient


# Replace the placeholder values with your actual database credentials
db_host = "127.0.0.1"
db_port = "3306"
db_user = "root"
db_password = "root4321"
db_name = "ResumeData"

# Establish a connection to the MySQL database
connection = mysql.connector.connect(
    host=db_host,
    port=db_port,
    user=db_user,
    password=db_password,
    database=db_name
)

# Create a cursor object from the database connection
cursor = connection.cursor()

# Parse the resume and extract information using Azure Form Recognizer
endpoint = "https://resume-parser.cognitiveservices.azure.com/"
key = "9fbd24c9f8864c488f665b479889f5a4"
model_id = "ResumeParser3"
file_path = "13.pdf"

document_analysis_client = DocumentAnalysisClient(
    endpoint=endpoint, credential=AzureKeyCredential(key)
)

# Replace with your own values
conn_str = "DefaultEndpointsProtocol=https;AccountName=resumedatasets;AccountKey=IxbqKU+zeXTlQJ6NbzhV28qO2gLU5zBM8WwguM/rKXagGv6xRjgj2pirUrIh+dQybPk9dT0lU67S+AStKbLNKw==;EndpointSuffix=core.windows.net"
container_name = "resume"


# Upload the file to Azure Blob Storage and get the URL
# You will need to create a BlobServiceClient and a container first
blob_service_client = BlobServiceClient.from_connection_string(conn_str)
container_client = blob_service_client.get_container_client(container_name)

# Generate a unique file name
import uuid
new_file_path = str(uuid.uuid4()) + ".pdf"

# Open the file in binary mode
with open(file_path, "rb") as f:
    # Upload the file to the container with the new file name
    blob_client = container_client.upload_blob(new_file_path, data=f)
    # Get the file URL
    file_url = blob_client.url

# Call the analyze document method with the URL
poller = document_analysis_client.begin_analyze_document_from_url(model_id, file_url)
result = poller.result()

# Assuming 'result' contains the extracted resume information

# Insert data into the Candidates table
insert_candidates_query = """
INSERT INTO Candidates (FirstName, LastName, EmailId, PhoneNumber, PhoneNumber2, LinkedInId, Language1, Language2) 
VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
"""

# Extract the relevant information from the parsed data
first_name = result.documents[0].fields.get("FirstName").value
last_name = result.documents[0].fields.get("LastName").value
email_id = result.documents[0].fields.get("Email Id").value
phone_number = result.documents[0].fields.get("Phone Number").value
phone_number2 = result.documents[0].fields.get("Phone Number2").value
linkedin_id = result.documents[0].fields.get("LinkedIn Id").value
language1 = result.documents[0].fields.get("Language1").value
language2 = result.documents[0].fields.get("Language2").value

# Execute the INSERT query for the Candidates table
cursor.execute(insert_candidates_query, (first_name, last_name, email_id, phone_number, phone_number2, linkedin_id, language1, language2))

# Get the last inserted candidate ID
candidate_id = cursor.lastrowid

#---------------------------------------------------------------------

# Insert data into the WorkExperience table
insert_experience_query = """
INSERT INTO WorkExperience (CandidateID, Title, Currently_Pursuing, Duration, Details) 
VALUES (%s, %s, %s, %s, %s)
"""

# Extract the relevant information from the parsed data
experience_field = result.documents[0].fields.get("WorkExperience")
if experience_field and experience_field.value is not None:
    for experience in experience_field.value:
        title = experience.value.get("Title")
        currently_pursuing = experience.value.get("Currently Pursuing")
        duration = experience.value.get("Duration")
        details = experience.value.get("Details")

        # Execute the INSERT query for each experience entry
        cursor.execute(insert_experience_query, (candidate_id, title, currently_pursuing, duration, details))
else:
    # Handle the case when "WorkExperience" field is not present or has no values
    title = None
    currently_pursuing = None
    duration = None
    details = None

    # Execute the INSERT query with None values for experience
    cursor.execute(insert_experience_query, (candidate_id, title, currently_pursuing, duration, details))

#-------------------------------------------------------------------------

# Insert data into the Education table
insert_education_query = """
INSERT INTO Education (CandidateID, Year, Degree, Branch, InstituteName, Grade) 
VALUES (%s, %s, %s, %s, %s, %s)
"""

# Extract the relevant information from the parsed data
education_field = result.documents[0].fields.get("Education")
if education_field and education_field.value is not None:
    for education in education_field.value:
        year = education.value.get("Year").value if education.value.get("Year") else None
        degree = education.value.get("Degree").value if education.value.get("Degree") else None
        branch = education.value.get("Branch").value if education.value.get("Branch") else None
        institute_name = education.value.get("InstituteName").value if education.value.get("InstituteName") else None
        grade = education.value.get("Grade").value if education.value.get("Grade") else None

        cursor.execute(insert_education_query, (candidate_id, year, degree, branch, institute_name, grade))
else:
    # Handle the case when "Education" field is not present or has no values
    year = None
    degree = None
    branch = None
    institute_name = None
    grade = None

    # Execute the INSERT query with None values for education
    cursor.execute(insert_education_query, (candidate_id, year, degree, branch, institute_name, grade))

#-----------------------------------------------------------------------

# Insert data into the Reference table
insert_reference_query = """
INSERT INTO Reference (CandidateID, Name, Designation, PhoneNumber, EmailId) 
VALUES (%s, %s, %s, %s, %s)
"""

# Extract the relevant information from the parsed data
reference_field = result.documents[0].fields.get("Reference")
if reference_field and reference_field.value is not None:
    for reference in reference_field.value:
        name = reference.value.get("Name")
        designation = reference.value.get("Designation")
        phone_number = reference.value.get("PhoneNumber")
        email_id = reference.value.get("EmailId")

        # Execute the INSERT query for each reference entry
        cursor.execute(insert_reference_query, (candidate_id, name, designation, phone_number, email_id))
else:
    # Handle the case when "Reference" field is not present or has no values
    name = None
    designation = None
    phone_number = None
    email_id = None

    # Execute the INSERT query with None values for reference
    cursor.execute(insert_reference_query, (candidate_id, name, designation, phone_number, email_id))

#------------------------------------------------------------------------

# Commit the changes to the database
connection.commit()

# Close the cursor and the database connection
cursor.close()
connection.close()

