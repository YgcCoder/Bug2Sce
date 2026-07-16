import fs from "node:fs/promises";
import { Workbook, SpreadsheetFile } from "@oai/artifact-tool";

const projectRoot = "<WORKSPACE_ROOT>";
const outDir = `${projectRoot}/processed/experiments/main_evaluation_prebatch`;
const csvPath = `${outDir}/phase3_360_manual_review_table.csv`;
const xlsxPath = `${outDir}/phase3_360_manual_review_table.xlsx`;
const previewPath = `${outDir}/phase3_360_manual_review_table_preview.png`;

const csvText = await fs.readFile(csvPath, "utf8");
const workbook = await Workbook.fromCSV(csvText, { sheetName: "Manual Review 360" });
const sheet = workbook.worksheets.getItem("Manual Review 360");

sheet.showGridLines = false;
sheet.freezePanes.freezeRows(1);
sheet.freezePanes.freezeColumns(3);

const used = sheet.getUsedRange();
const rowCount = used.rowCount;
const colCount = used.columnCount;
const header = sheet.getRangeByIndexes(0, 0, 1, colCount);
header.format.fill.color = "#1F4E78";
header.format.font.color = "#FFFFFF";
header.format.font.bold = true;
header.format.wrapText = true;
header.format.horizontalAlignment = "center";
header.format.verticalAlignment = "center";

const autoRange = sheet.getRangeByIndexes(0, 0, rowCount, 28);
autoRange.format.borders = { preset: "inside", style: "thin", color: "#D9E2F3" };

const manualRange = sheet.getRangeByIndexes(0, 28, rowCount, 9);
manualRange.format.fill.color = "#FFF2CC";
manualRange.format.borders = { preset: "inside", style: "thin", color: "#D6B656" };

const manualHeader = sheet.getRangeByIndexes(0, 28, 1, 9);
manualHeader.format.fill.color = "#B45F06";
manualHeader.format.font.color = "#FFFFFF";
manualHeader.format.font.bold = true;

// Data validation for human-editable columns.
sheet.getRange(`AC2:AC${rowCount}`).dataValidation = {
  rule: {
    type: "list",
    values: [
      "same-root-cause failure",
      "different-failure scenario",
      "no-failure scenario",
      "invalid scenario",
      "unknown",
      "needs review",
    ],
  },
};
sheet.getRange(`AD2:AD${rowCount}`).dataValidation = {
  rule: { type: "list", values: ["yes", "no", "uncertain"] },
};
sheet.getRange(`AF2:AF${rowCount}`).dataValidation = {
  rule: { type: "list", values: ["high", "medium", "low"] },
};
sheet.getRange(`AG2:AG${rowCount}`).dataValidation = {
  rule: { type: "list", values: ["yes", "no"] },
};
sheet.getRange(`AJ2:AJ${rowCount}`).dataValidation = {
  rule: {
    type: "list",
    values: [
      "keep_as_positive_if_confirmed",
      "regenerate_with_stricter_oracle_match",
      "regenerate_with_constraints",
      "repair_and_regenerate",
      "review_then_decide",
      "optional_regenerate",
      "discard",
    ],
  },
};

// Set practical widths. Keep long evidence columns readable but not enormous.
const widths = [
  12, 10, 42, 10, 10, 28, 12, 16, 16, 24, 26, 28, 34, 14,
  9, 9, 9, 10, 10, 16, 10, 12, 10, 12, 28, 42, 54, 54,
  28, 18, 18, 16, 14, 16, 46, 32, 48,
];
for (let i = 0; i < widths.length; i += 1) {
  sheet.getRangeByIndexes(0, i, rowCount, 1).format.columnWidth = widths[i];
}
sheet.getRangeByIndexes(1, 0, rowCount - 1, colCount).format.verticalAlignment = "top";
sheet.getRangeByIndexes(1, 24, rowCount - 1, 13).format.wrapText = true;

// Summary sheet for quick orientation.
const summary = workbook.worksheets.add("Review Guide");
summary.showGridLines = false;
summary.getRange("A1:D1").values = [["Phase 3 Manual Review Guide", "", "", ""]];
summary.getRange("A1:D1").merge();
summary.getRange("A1").format.fill.color = "#1F4E78";
summary.getRange("A1").format.font.color = "#FFFFFF";
summary.getRange("A1").format.font.bold = true;
summary.getRange("A1").format.font.size = 16;

summary.getRange("A3:B12").values = [
  ["Purpose", "Review all 360 Phase 3 candidates before the next LLM regeneration loop."],
  ["Manual final category", "same-root-cause failure / different-failure scenario / no-failure scenario / invalid scenario / unknown."],
  ["manual_same_root_cause", "yes / no / uncertain."],
  ["manual_failure_type", "Use C/S/L/R combinations or concise free text."],
  ["manual_confidence", "high / medium / low."],
  ["manual_checked", "Set to yes when reviewed."],
  ["manual_notes", "Write the concrete evidence or uncertainty."],
  ["loop2_action", "Keep, repair, regenerate, discard, or review later."],
  ["Important", "Auto labels are triage only. Same-root-cause requires human confirmation."],
  ["Source", csvPath],
];
summary.getRange("A3:A12").format.font.bold = true;
summary.getRange("A3:B12").format.wrapText = true;
summary.getRange("A3:B12").format.borders = { preset: "inside", style: "thin", color: "#D9E2F3" };
summary.getRange("A3:B12").format.columnWidth = 32;
summary.getRange("B3:B12").format.columnWidth = 88;

const inspect = await workbook.inspect({
  kind: "sheet,region",
  sheetId: "Manual Review 360",
  range: "A1:AK8",
  maxChars: 4000,
});
console.log(inspect.ndjson);

const preview = await workbook.render({
  sheetName: "Manual Review 360",
  range: "A1:AK18",
  scale: 1,
  format: "png",
});
await fs.writeFile(previewPath, new Uint8Array(await preview.arrayBuffer()));

const output = await SpreadsheetFile.exportXlsx(workbook);
await output.save(xlsxPath);
console.log(xlsxPath);
