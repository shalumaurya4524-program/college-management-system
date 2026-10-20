document.addEventListener("DOMContentLoaded", () => {
  const search = document.getElementById("tableSearch");
  const table = document.getElementById("dataTable");
  if (search && table) {
    search.addEventListener("input", () => {
      const term = search.value.toLowerCase().trim();
      table.querySelectorAll("tbody tr").forEach(row => {
        row.style.display = row.innerText.toLowerCase().includes(term) ? "" : "none";
      });
    });
  }
});
