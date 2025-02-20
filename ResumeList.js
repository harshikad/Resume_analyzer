import { useState, useEffect } from "react";
import axios from "axios";
import { List, ListItem, ListItemText } from "@mui/material";

const ResumeList = () => {
  const [resumes, setResumes] = useState([]);

  useEffect(() => {
    axios.get("http://127.0.0.1:8000/get_resumes/")
      .then(response => setResumes(response.data))
      .catch(error => console.error("Error fetching resumes:", error));
  }, []);

  return (
    <div>
      <h2>Uploaded Resumes</h2>
      <List>
        {resumes.length > 0 ? (
          resumes.map((resume) => (
            <ListItem key={resume.id}>
              <ListItemText primary={resume.file_name} secondary={JSON.stringify(resume)} />
            </ListItem>
          ))
        ) : (
          <p>No resumes found.</p>
        )}
      </List>
    </div>
  );
};

export default ResumeList;
