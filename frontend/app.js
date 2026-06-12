const state = {
  data: null,
};

const elements = {
  metricsGrid: document.getElementById("metrics-grid"),
  recentMessages: document.getElementById("recent-messages"),
  taskSummary: document.getElementById("task-summary"),
  documentsTable: document.getElementById("documents-table"),
  tasksTable: document.getElementById("tasks-table"),
  productsTable: document.getElementById("products-table"),
  reportsTable: document.getElementById("reports-table"),
  automationTable: document.getElementById("automation-table"),
  workflowForm: document.getElementById("workflow-form"),
  workflowResult: document.getElementById("workflow-result"),
  reportForm: document.getElementById("report-form"),
  automationResult: document.getElementById("automation-result"),
  generateReportOnly: document.getElementById("generate-report-only"),
  refreshButton: document.getElementById("refresh-dashboard"),
  sendEmail: document.getElementById("send-email"),
  reportEmail: document.getElementById("report-email"),
  reportDate: document.getElementById("report-date"),
  toast: document.getElementById("toast"),
  navLinks: Array.from(document.querySelectorAll(".nav-link")),
  panels: Array.from(document.querySelectorAll("[data-panel-content]")),
};

function showToast(message, tone = "success") {
  elements.toast.textContent = message;
  elements.toast.classList.remove("hidden");
  elements.toast.style.background = tone === "error" ? "#8d3923" : "#183e2f";
  window.clearTimeout(showToast.timeoutId);
  showToast.timeoutId = window.setTimeout(() => {
    elements.toast.classList.add("hidden");
  }, 3200);
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function formatMetrics(metrics) {
  const items = [
    ["Messages", metrics.total_messages, "Captured by the AI intake layer"],
    ["Orders", metrics.total_orders, "Commercial workflows created"],
    ["Documents", metrics.total_documents, "Invoices and quotations issued"],
    ["Open Tasks", metrics.open_tasks, "Operational work still pending"],
    ["Revenue (AED)", metrics.total_revenue, "Document value currently tracked"],
  ];

  elements.metricsGrid.innerHTML = items
    .map(
      ([label, value, note]) => `
        <article class="metric-card">
          <p class="metric-label">${label}</p>
          <div class="metric-value">${escapeHtml(value)}</div>
          <div class="metric-note">${note}</div>
        </article>
      `
    )
    .join("");
}

function renderTable(container, rows, columns) {
  if (!rows || rows.length === 0) {
    container.innerHTML = '<div class="empty-state">No records available yet.</div>';
    return;
  }

  const thead = columns.map((column) => `<th>${escapeHtml(column.label)}</th>`).join("");
  const tbody = rows
    .map(
      (row) => `
        <tr>
          ${columns
            .map((column) => `<td>${escapeHtml(row[column.key] ?? "-")}</td>`)
            .join("")}
        </tr>
      `
    )
    .join("");

  container.innerHTML = `
    <table>
      <thead><tr>${thead}</tr></thead>
      <tbody>${tbody}</tbody>
    </table>
  `;
}

function renderTaskSummary(tasks) {
  if (!tasks || tasks.length === 0) {
    elements.taskSummary.innerHTML = '<div class="empty-state">No tasks generated yet.</div>';
    return;
  }

  const counts = tasks.reduce((accumulator, task) => {
    const key = task.priority || "unknown";
    accumulator[key] = (accumulator[key] || 0) + 1;
    return accumulator;
  }, {});

  elements.taskSummary.innerHTML = Object.entries(counts)
    .map(
      ([label, value]) => `
        <div class="stat-row">
          <span>${escapeHtml(label)}</span>
          <strong>${escapeHtml(value)}</strong>
        </div>
      `
    )
    .join("");
}

function renderDashboard(data) {
  state.data = data;
  formatMetrics(data.metrics);
  renderTable(elements.recentMessages, data.messages.slice(0, 6), [
    { key: "customer", label: "Customer" },
    { key: "intent", label: "Intent" },
    { key: "confidence", label: "Confidence" },
    { key: "status", label: "Status" },
    { key: "created_at", label: "Created" },
  ]);
  renderTaskSummary(data.tasks);
  renderTable(elements.documentsTable, data.documents, [
    { key: "invoice_number", label: "Number" },
    { key: "document_type", label: "Type" },
    { key: "customer", label: "Customer" },
    { key: "total_amount", label: "Total" },
    { key: "issue_date", label: "Issue Date" },
  ]);
  renderTable(elements.tasksTable, data.tasks, [
    { key: "title", label: "Task" },
    { key: "task_type", label: "Type" },
    { key: "priority", label: "Priority" },
    { key: "status", label: "Status" },
    { key: "customer", label: "Customer" },
  ]);
  renderTable(elements.productsTable, data.products.slice(0, 12), [
    { key: "sku", label: "SKU" },
    { key: "name", label: "Name" },
    { key: "category", label: "Category" },
    { key: "unit_price", label: "Price" },
  ]);
  renderTable(elements.reportsTable, data.reports, [
    { key: "report_date", label: "Date" },
    { key: "total_messages", label: "Messages" },
    { key: "total_orders", label: "Orders" },
    { key: "total_revenue", label: "Revenue" },
    { key: "sent_via", label: "Sent Via" },
  ]);
  renderTable(elements.automationTable, data.automation_logs, [
    { key: "event_type", label: "Event" },
    { key: "status", label: "Status" },
    { key: "target_system", label: "Target" },
    { key: "created_at", label: "Created" },
  ]);
}

async function loadDashboard() {
  const response = await fetch("/ui/data");
  if (!response.ok) {
    throw new Error("Failed to load dashboard data.");
  }
  const data = await response.json();
  renderDashboard(data);
}

function renderWorkflowResult(result) {
  const matchedItems = result.matched_items
    .map(
      (item) => `
        <tr>
          <td>${escapeHtml(item.name)}</td>
          <td>${escapeHtml(item.quantity)}</td>
          <td>${escapeHtml(item.unit_price)}</td>
          <td>${escapeHtml(item.line_total)}</td>
        </tr>
      `
    )
    .join("");

  const generatedTasks = result.generated_tasks
    .map(
      (task) => `
        <li><strong>${escapeHtml(task.title)}</strong> <span class="badge gold">${escapeHtml(task.priority)}</span></li>
      `
    )
    .join("");

  elements.workflowResult.innerHTML = `
    <div class="result-card">
      <h4>Extraction Summary</h4>
      <p><strong>Intent:</strong> ${escapeHtml(result.extraction.intent)}</p>
      <p><strong>Need:</strong> ${escapeHtml(result.extraction.customer_need)}</p>
      <p><strong>Suggested reply:</strong> ${escapeHtml(result.suggested_customer_reply)}</p>
    </div>
    <div class="result-card">
      <h4>Pricing</h4>
      <p><span class="badge green">${escapeHtml(result.document.document_type)}</span> ${escapeHtml(result.document.invoice_number)}</p>
      <p>Subtotal: AED ${escapeHtml(result.pricing.subtotal)}</p>
      <p>Delivery fee: AED ${escapeHtml(result.pricing.delivery_fee)}</p>
      <p>Total: AED ${escapeHtml(result.pricing.total_amount)}</p>
    </div>
    <div class="result-card">
      <h4>Matched Items</h4>
      <table>
        <thead><tr><th>Item</th><th>Qty</th><th>Unit Price</th><th>Line Total</th></tr></thead>
        <tbody>${matchedItems || '<tr><td colspan="4">No matched items.</td></tr>'}</tbody>
      </table>
    </div>
    <div class="result-card">
      <h4>Generated Tasks</h4>
      <ul>${generatedTasks || "<li>No tasks generated.</li>"}</ul>
    </div>
    <div class="result-card">
      <h4>Invoice Preview</h4>
      <div class="html-preview">
        <iframe id="workflow-preview-frame"></iframe>
      </div>
    </div>
  `;

  const previewFrame = document.getElementById("workflow-preview-frame");
  if (previewFrame) {
    previewFrame.srcdoc = result.invoice_html;
  }
}

function renderAutomationResult(result, modeLabel) {
  const logs = (result.automation_logs || [result.automation_log])
    .filter(Boolean)
    .map(
      (log) => `
        <li><strong>${escapeHtml(log.event_type)}</strong> -> ${escapeHtml(log.status)} (${escapeHtml(log.target_system)})</li>
      `
    )
    .join("");

  elements.automationResult.innerHTML = `
    <div class="result-card">
      <h4>${escapeHtml(modeLabel)} completed</h4>
      <p><strong>Report date:</strong> ${escapeHtml(result.report.report_date)}</p>
      <p><strong>Messages:</strong> ${escapeHtml(result.report.total_messages)}</p>
      <p><strong>Orders:</strong> ${escapeHtml(result.report.total_orders)}</p>
      <p><strong>Documents:</strong> ${escapeHtml(result.report.total_invoices)}</p>
      <p><strong>Revenue:</strong> AED ${escapeHtml(result.report.total_revenue)}</p>
      <p><strong>Open tasks:</strong> ${escapeHtml(result.open_tasks)}</p>
      <p><strong>Email sent:</strong> ${escapeHtml(result.email_sent ?? false)}</p>
    </div>
    <div class="result-card">
      <h4>Automation Logs</h4>
      <ul>${logs || "<li>No automation log rows returned.</li>"}</ul>
    </div>
  `;
}

async function handleWorkflowSubmit(event) {
  event.preventDefault();
  const payload = {
    message_text: document.getElementById("message-text").value.trim(),
    customer_name: document.getElementById("customer-name").value.trim() || null,
    customer_phone: document.getElementById("customer-phone").value.trim() || null,
    customer_email: document.getElementById("customer-email").value.trim() || null,
    document_type: document.getElementById("document-type").value || null,
  };

  if (!payload.message_text) {
    showToast("Enter a customer message first.", "error");
    return;
  }

  const response = await fetch("/orders/from-message", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  const result = await response.json();
  if (!response.ok) {
    showToast(result.detail || "Workflow request failed.", "error");
    return;
  }

  renderWorkflowResult(result);
  await loadDashboard();
  showToast("Workflow processed successfully.");
}

async function runGenerateOnly() {
  const payload = {
    report_date: elements.reportDate.value || null,
  };
  const response = await fetch("/reports/generate", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  const result = await response.json();
  if (!response.ok) {
    showToast(result.detail || "Report generation failed.", "error");
    return;
  }

  renderAutomationResult(result, "Daily report generation");
  await loadDashboard();
  showToast("Daily report generated.");
}

async function handleAutomationSubmit(event) {
  event.preventDefault();
  const secret = document.getElementById("webhook-secret").value.trim();
  if (!secret) {
    showToast("Enter the webhook secret before triggering automation.", "error");
    return;
  }

  const payload = {
    report_date: elements.reportDate.value || null,
    recipient_email: elements.reportEmail.value.trim() || null,
    send_email: elements.sendEmail.checked,
  };

  const response = await fetch("/automation/daily-report", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "x-webhook-secret": secret,
    },
    body: JSON.stringify(payload),
  });
  const result = await response.json();
  if (!response.ok) {
    showToast(result.detail || "Automation trigger failed.", "error");
    return;
  }

  renderAutomationResult(result, "Automation run");
  await loadDashboard();
  showToast("Automation triggered successfully.");
}

function bindNavigation() {
  elements.navLinks.forEach((link) => {
    link.addEventListener("click", () => {
      const panel = link.dataset.panel;
      elements.navLinks.forEach((item) => item.classList.toggle("is-active", item === link));
      elements.panels.forEach((section) => {
        section.classList.toggle("hidden", section.dataset.panelContent !== panel);
      });
    });
  });
}

function initDefaultReportDate() {
  const today = new Date().toISOString().slice(0, 10);
  elements.reportDate.value = today;
}

async function init() {
  bindNavigation();
  initDefaultReportDate();
  elements.workflowForm.addEventListener("submit", handleWorkflowSubmit);
  elements.reportForm.addEventListener("submit", handleAutomationSubmit);
  elements.generateReportOnly.addEventListener("click", runGenerateOnly);
  elements.refreshButton.addEventListener("click", async () => {
    await loadDashboard();
    showToast("Live data refreshed.");
  });

  try {
    await loadDashboard();
  } catch (error) {
    console.error(error);
    showToast("Failed to load the dashboard data.", "error");
  }
}

init();
