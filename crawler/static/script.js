document.addEventListener("DOMContentLoaded", function () {
    fetch('/jobs')
        .then(response => response.json())
        .then(data => {
            const jobList = document.getElementById("job-list");

            data.forEach(job => {
                const listItem = document.createElement("li");
                listItem.innerHTML = `<strong>${job.company_name}</strong>: <a href="${job.link}" target="_blank">${job.title}</a>`;
                jobList.appendChild(listItem);
            });
        })
        .catch(error => console.error("Error fetching job data:", error));
});