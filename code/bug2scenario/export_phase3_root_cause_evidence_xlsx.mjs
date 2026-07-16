import fs from "node:fs/promises";
import { Workbook, SpreadsheetFile } from "@oai/artifact-tool";

const projectRoot = "<WORKSPACE_ROOT>";
const outDir = `${projectRoot}/processed/experiments/main_evaluation_prebatch`;
const csvPath = `${outDir}/phase3_360_root_cause_evidence_table.csv`;
const xlsxPath = `${outDir}/phase3_360_root_cause_evidence_table.xlsx`;
const previewPath = `${outDir}/phase3_360_root_cause_evidence_table_preview.png`;

const csvText = await fs.readFile(csvPath, "utf8");
const workbook = await Workbook.fromCSV(csvText, { sheetName: "Code Evidence 360" });
const sheet = workbook.worksheets.getItem("Code Evidence 360");

sheet.showGridLines = false;
sheet.freezePanes.freezeRows(1);
sheet.freezePanes.freezeColumns(4);

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

// A:AB automatic execution triage, AC:AG code root-cause evidence, AH:AP manual columns.
sheet.getRangeByIndexes(0, 0, rowCount, 28).format.borders = { preset: "inside", style: "thin", color: "#D9E2F3" };
const evidenceRange = sheet.getRangeByIndexes(0, 28, rowCount, 5);
evidenceRange.format.fill.color = "#E2F0D9";
evidenceRange.format.borders = { preset: "inside", style: "thin", color: "#70AD47" };
const evidenceHeader = sheet.getRangeByIndexes(0, 28, 1, 5);
evidenceHeader.format.fill.color = "#548235";
evidenceHeader.format.font.color = "#FFFFFF";
evidenceHeader.format.font.bold = true;

const manualRange = sheet.getRangeByIndexes(0, 33, rowCount, 9);
manualRange.format.fill.color = "#FFF2CC";
manualRange.format.borders = { preset: "inside", style: "thin", color: "#D6B656" };
const manualHeader = sheet.getRangeByIndexes(0, 33, 1, 9);
manualHeader.format.fill.color = "#B45F06";
manualHeader.format.font.color = "#FFFFFF";
manualHeader.format.font.bold = true;

sheet.getRange(`AD2:AD${rowCount}`).dataValidation = {
  rule: {
    type: "list",
    values: [
      "likely_same_root_cause_by_code",
      "possible_same_root_cause_needs_video",
      "likely_different_root_cause",
      "likely_different_or_weak_evidence",
      "likely_no_failure_or_no_oracle",
      "invalid_scenario",
      "unknown_hang",
      "no_trace_json_for_code_check",
    ],
  },
};
sheet.getRange(`AE2:AE${rowCount}`).dataValidation = {
  rule: { type: "list", values: ["high", "medium", "low"] },
};
sheet.getRange(`AH2:AH${rowCount}`).dataValidation = {
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
sheet.getRange(`AI2:AI${rowCount}`).dataValidation = {
  rule: { type: "list", values: ["yes", "no", "uncertain"] },
};
sheet.getRange(`AK2:AK${rowCount}`).dataValidation = {
  rule: { type: "list", values: ["high", "medium", "low"] },
};
sheet.getRange(`AL2:AL${rowCount}`).dataValidation = {
  rule: { type: "list", values: ["yes", "no"] },
};
sheet.getRange(`AO2:AO${rowCount}`).dataValidation = {
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

const widths = [
  12, 10, 42, 10, 10, 28, 12, 16, 16, 24, 26, 28, 34, 14,
  9, 9, 9, 10, 10, 16, 10, 12, 10, 12, 28, 42, 54, 54,
  54, 34, 16, 12, 96,
  28, 18, 18, 16, 14, 16, 46, 32, 48,
];
for (let i = 0; i < widths.length; i += 1) {
  sheet.getRangeByIndexes(0, i, rowCount, 1).format.columnWidth = widths[i];
}
sheet.getRangeByIndexes(1, 0, rowCount - 1, colCount).format.verticalAlignment = "top";
sheet.getRangeByIndexes(1, 24, rowCount - 1, 18).format.wrapText = true;

const guide = workbook.worksheets.add("Review Guide");
guide.showGridLines = false;
guide.getRange("A1:D1").values = [["Phase 3 Code-assisted Root-Cause Review", "", "", ""]];
guide.getRange("A1:D1").merge();
guide.getRange("A1").format.fill.color = "#1F4E78";
guide.getRange("A1").format.font.color = "#FFFFFF";
guide.getRange("A1").format.font.bold = true;
guide.getRange("A1").format.font.size = 16;

guide.getRange("A3:B13").values = [
  ["Purpose", "Use code evidence to triage all 360 candidates before human video inspection."],
  ["Green columns", "Automatic root-cause evidence from original DriveFuzz bug JSON and candidate execution JSON."],
  ["likely_same_root_cause_by_code", "Oracle and structural evidence support same-root-cause; spot-check video if needed."],
  ["possible_same_root_cause_needs_video", "Some code evidence matches, but video/manual check is needed."],
  ["likely_different_root_cause", "Observed oracle symptom differs from the expected bug family."],
  ["likely_no_failure_or_no_oracle", "No observed DriveFuzz oracle in the parsed execution JSON."],
  ["invalid_scenario", "Spawn or execution validity failure; cannot count as same-root-cause."],
  ["Manual columns", "Use yellow columns for final classification after video/log checks."],
  ["Important", "Code evidence is triage only. The paper should describe this as code-assisted post-execution classification."],
  ["Source CSV", csvPath],
  ["Output XLSX", xlsxPath],
];
guide.getRange("A3:A13").format.font.bold = true;
guide.getRange("A3:B13").format.wrapText = true;
guide.getRange("A3:B13").format.borders = { preset: "inside", style: "thin", color: "#D9E2F3" };
guide.getRange("A3:B13").format.columnWidth = 34;
guide.getRange("B3:B13").format.columnWidth = 94;

const inspect = await workbook.inspect({
  kind: "sheet,region",
  sheetId: "Code Evidence 360",
  range: "A1:AP8",
  maxChars: 4000,
});
console.log(inspect.ndjson);

const preview = await workbook.render({
  sheetName: "Code Evidence 360",
  range: "A1:AP18",
  scale: 1,
  format: "png",
});
await fs.writeFile(previewPath, new Uint8Array(await preview.arrayBuffer()));

const output = await SpreadsheetFile.exportXlsx(workbook);
await output.save(xlsxPath);
console.log(xlsxPath);
