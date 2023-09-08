
create database ResumeData;

Use ResumeData;

-- Create the Candidates table
CREATE TABLE Candidates (
  CandidateID INT AUTO_INCREMENT PRIMARY KEY,
  FirstName VARCHAR(255),
  LastName VARCHAR(255),
  EmailId VARCHAR(255),
  PhoneNumber VARCHAR(255),
  PhoneNumber2 VARCHAR(255),
  LinkedInId VARCHAR(255),
  Language1 VARCHAR(255),
  Language2 VARCHAR(255)
);

-- Create the WorkExperience table
CREATE TABLE WorkExperience (
  ExperienceID INT AUTO_INCREMENT PRIMARY KEY,
  CandidateID INT,
  Title VARCHAR(255),
  Currently_Pursuing VARCHAR(255),
  Duration VARCHAR(255),
  Details VARCHAR(255),
  FOREIGN KEY (CandidateID) REFERENCES Candidates(CandidateID)
);

-- Create the Education table


CREATE TABLE Education (
  EducationID INT AUTO_INCREMENT PRIMARY KEY,
  CandidateID INT,
  Year VARCHAR(255),
  Degree VARCHAR(255),
  InstituteName VARCHAR(255),
  Grade VARCHAR(255),
  FOREIGN KEY (CandidateID) REFERENCES Candidates(CandidateID)
);

-- Create the Reference table
CREATE TABLE Reference (
  ReferenceID INT AUTO_INCREMENT PRIMARY KEY,
  CandidateID INT,
  Name VARCHAR(255),
  Designation VARCHAR(255),
  PhoneNumber VARCHAR(255),
  EmailId VARCHAR(255),
  FOREIGN KEY (CandidateID) REFERENCES Candidates(CandidateID)
);

ALTER TABLE Education
ADD COLUMN Branch VARCHAR(200) AFTER Degree;
