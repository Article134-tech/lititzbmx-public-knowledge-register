document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll("[data-table-filter]").forEach(input => {
    const tableId = input.getAttribute("data-table-filter");
    const table = document.getElementById(tableId);
    if (!table) return;
    input.addEventListener("input", () => {
      const query = input.value.trim().toLowerCase();
      table.querySelectorAll("tbody tr").forEach(row => {
        row.hidden = query && !row.textContent.toLowerCase().includes(query);
      });
    });
  });
});
