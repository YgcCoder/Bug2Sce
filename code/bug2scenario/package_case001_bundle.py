#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import shutil
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path("<WORKSPACE_ROOT>")
BUNDLE_NAME = "Bug2Scenario_case001_evidence_bundle"
BUNDLE_ROOT = PROJECT_ROOT / BUNDLE_NAME
EXTERNAL_ROOT = Path("<REMOVABLE_MEDIA_ROOT>") / BUNDLE_NAME

SOURCE_SCENARIO_USED = Path("<REMOVABLE_MEDIA_ROOT>/scenario-001.json")
SOURCE_SCENARIO_ZIP = Path("<PRIVATE_SOURCE_ROOT>/seed-artifact-case_001.zip")
SOURCE_BATCH_ROOT = Path("<REMOVABLE_MEDIA_ROOT>/batch-001-003.3")
SOURCE_META = SOURCE_BATCH_ROOT / "meta"
SOURCE_QUEUE = SOURCE_BATCH_ROOT / "queue/1_1_1_1781163442.1472487.json"
SOURCE_ERROR = SOURCE_BATCH_ROOT / "errors/1_1_1_1781163442.1472487.json"
SOURCE_BAG = SOURCE_BATCH_ROOT / "rosbags/1_1_1_1781163442.1472487.bag"

SOURCE_PROMPT = PROJECT_ROOT / "processed/prompts/proposal_v2/case_001_prompt.md"
SOURCE_LLM_OUTPUT = PROJECT_ROOT / "processed/manual_llm_results/proposal/case_001_raw_response.md"
SOURCE_LLM_INPUT = PROJECT_ROOT / "processed/llm_inputs/case_001.json"
SOURCE_CRITICAL_WINDOW = PROJECT_ROOT / "processed/critical_windows/case_001_critical_window.json"
SOURCE_EXPORT_SCRIPT = PROJECT_ROOT / "scripts/export_runnable_seed.py"


def read_text(path: Path) -> str:
    return path.read_text()


def read_json(path: Path) -> Any:
    return json.loads(path.read_text())


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)


def write_json(path: Path, payload: Any) -> None:
    write_text(path, json.dumps(payload, indent=2, ensure_ascii=False) + "\n")


def short_json(data: Any, max_chars: int = 1200) -> str:
    text = json.dumps(data, indent=2, ensure_ascii=False)
    if len(text) <= max_chars:
        return text
    return text[: max_chars - 18] + "\n... [truncated]\n"


def copy_if_exists(src: Path, dst: Path) -> bool:
    if not src.exists():
        return False
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
    return True


def prepare_root(root: Path) -> None:
    if root.exists():
        shutil.rmtree(root)
    (root / "01_case001_runnable_json").mkdir(parents=True)
    (root / "02_execution_evidence" / "screenshots").mkdir(parents=True)
    (root / "03_llm_causal_explanation").mkdir(parents=True)
    (root / "04_next_steps").mkdir(parents=True)
    (root / "scripts").mkdir(parents=True)


def build_json_description() -> str:
    return "\n".join(
        [
            "# JSON 说明",
            "",
            "- 文件名：`scenario-case_001.json`",
            "- 类型：`与 DriveFuzz 输入 schema 对齐、可运行的 DriveFuzz-style scenario JSON`",
            "- 来源：基于 `case_001` 原始 failure seed 以及当时本地真实运行时使用的 JSON 整理/重构得到。",
            "- 目的：证明已知 bug case 可以被整理成真实可运行的 DriveFuzz 输入。",
            "- 这里不做的宣称：",
            "  - 这不是 baseline 实验结果",
            "  - 这不是已经验证过的 amplified new scenario",
            "  - 目前只证明它能跑通，还没继续验证它和原始 bug 的根因是不是同一类",
            "",
            "当前这个 JSON 的用途仅限于 execution-level feasibility validation。",
            "",
        ]
    )


def build_run_log_excerpt(meta_text: str, error_json: dict[str, Any], bag_path: Path) -> str:
    events = error_json.get("events", {})
    return "\n".join(
        [
            "# 运行证据摘录",
            "",
            "## 自动恢复出的运行命令",
            meta_text.strip(),
            "",
            "## 从执行产物中恢复出的关键 oracle 信号",
            f"- error json 路径：`{SOURCE_ERROR}`",
            f"- crash：`{events.get('crash')}`",
            f"- stuck：`{events.get('stuck')}`",
            f"- lane_invasion：`{events.get('lane_invasion')}`",
            f"- red：`{events.get('red')}`",
            f"- speeding：`{events.get('speeding')}`",
            f"- elapsed_time：`{error_json.get('elapsed_time')}`",
            f"- num_frames：`{error_json.get('num_frames')}`",
            f"- 检测到 rosbag 文件：`{bag_path}`",
            "",
            "## 说明",
            "",
            "- 当前可访问的文件快照里，没有自动恢复出一整份完整 stdout/stderr 控制台日志。",
            "- 当前摘录只基于保留下来的 `meta`、`errors/*.json` 和 rosbag 路径等执行产物整理而来。",
            "",
        ]
    )


def build_oracle_summary(error_json: dict[str, Any], bag_path: Path) -> str:
    events = error_json.get("events", {})
    status = "检测到 Collision" if events.get("crash") else "未发现 collision 标记"
    return "\n".join(
        [
            "# Oracle 结果总结",
            "",
            f"- Case ID：`case_001`",
            f"- DriveFuzz oracle 结果：`{status}`",
            f"- events.crash：`{events.get('crash')}`",
            f"- events.red：`{events.get('red')}`",
            f"- events.lane_invasion：`{events.get('lane_invasion')}`",
            f"- events.stuck：`{events.get('stuck')}`",
            f"- events.speeding：`{events.get('speeding')}`",
            f"- 是否生成 bag：`{'yes' if bag_path.exists() else 'no'}`",
            "",
            "当前结论：这个 runnable JSON 已经被本地执行链路接受并实际运行，且保留下来了至少 oracle-level 的 collision 证据。",
            "",
        ]
    )


def build_input_scenario_markdown(llm_input: dict[str, Any], critical: dict[str, Any]) -> str:
    compact = {
        "case_id": llm_input["case_id"],
        "fault_label": llm_input["fault_label"],
        "scenario_config": llm_input["scenario_config"],
        "oracle_consistency_status": critical.get("oracle_consistency_status"),
        "error_json_events": critical.get("error_json_events"),
        "critical_window_summary": critical.get("collision_window"),
    }
    return "\n".join(
        [
            "# 输入的 Scenario Data + Fault Label",
            "",
            "这个文件记录了用于支持 `case_001` 的 LLM causal explanation 的最小结构化输入。",
            "",
            "```json",
            short_json(compact, max_chars=5000),
            "```",
            "",
        ]
    )


def extract_root_cause_draft(raw_response: str) -> str:
    cleaned = raw_response.strip()
    if cleaned.startswith("# Paste raw webpage response"):
        cleaned = cleaned.split("\n", 1)[1].strip()
    try:
        parsed = json.loads(cleaned)
    except Exception:
        return "\n".join(
            [
                "# Root-Cause Pattern 草稿",
                "",
                "TODO：请后续人工解析保存下来的 LLM 输出，并在这里总结 candidate root-cause pattern。",
                "",
            ]
        )
    pattern = parsed.get("possible_root_cause_pattern", "unknown")
    chain = parsed.get("causal_chain", [])
    uncertainty = parsed.get("uncertain_or_missing_evidence", [])
    return "\n".join(
        [
            "# Root-Cause Pattern 草稿",
            "",
            "这个草稿是从当前真实保存的 `case_001` LLM causal explanation 中提取出来的。",
            "它目前只是一个工作假设，后面还需要再验证和原始 case 的根因是否一致。",
            "",
            f"- Candidate pattern：`{pattern}`",
            "",
            "## 支撑链条",
            "",
            *[f"- {item}" for item in chain],
            "",
            "## 主要不确定性",
            "",
            *[f"- {item}" for item in uncertainty[:8]],
            "",
        ]
    )


def build_readme() -> str:
    return "\n".join(
        [
            "# Bug2Scenario case_001 证据包",
            "",
            "这个 bundle 只用于展示 `case_001` 的最小工程证据链。",
            "这里不包含论文 draft、reference list 或 contribution 写作内容。",
            "",
            "## 当前状态",
            "",
            "- `case_001` 已完成 execution-level feasibility 验证。",
            "- 这个 runnable DriveFuzz-style JSON 已经可以在真实本地 `DriveFuzz + Autoware + CARLA` 环境中被加载并执行。",
            "- 当前保留下来的执行产物表明，DriveFuzz collision oracle 被触发，并且生成了 rosbag。",
            "- 目前先说明这个 case 能跑通并触发 oracle；它和原始 bug 的根因是否一致，还需要后续再验证。",
            "",
            "## 目录结构说明",
            "",
            "- `01_case001_runnable_json/`：可运行 JSON 以及它的说明",
            "- `02_execution_evidence/`：运行命令、执行证据摘录、oracle 结果总结、rosbag 路径/信息、截图占位",
            "- `03_llm_causal_explanation/`：scenario 输入、prompt、真实保存的 LLM 输出或 TODO 占位、root-cause pattern 草稿",
            "- `04_next_steps/`：Bug2Scenario 下一步实验计划",
            "- `scripts/`：当前用于生成或整理这个证据包的辅助脚本",
            "",
        ]
    )


def build_next_steps() -> str:
    return "\n".join(
        [
            "# 下一步实验计划",
            "",
            "1. 先完成 `case_001`、`case_024`、`case_027`、`case_013` 的 causal explanation。",
            "2. 从每个 case 中抽取一个保守的 root-cause pattern，并把 uncertainty 明确保留下来。",
            "3. 基于 root-cause pattern 生成 candidate amplified scenarios，而不是直接把当前 runnable JSON 当成 amplified scenario。",
            "4. 在执行前加入 rule-based validation，过滤掉物理上不合法或语义上不一致的候选场景。",
            "5. 将通过 validation 的候选场景重新放回 `DriveFuzz + Autoware + CARLA` 执行。",
            "6. 将 proposed Bug2Scenario pipeline 与不使用 root-cause-guided evidence 的 pure LLM baseline 做对比。",
            "7. 只有完成这些步骤后，才进一步评估某个 candidate 是否属于 same-root-cause failure family。",
            "",
        ]
    )


def build_llm_todo_or_output(raw_response: str) -> str:
    return "\n".join(
        [
            "# LLM 输出示例或 TODO",
            "",
            "下面放的是当前已经真实保存下来的 `case_001` 网页端模型输出。",
            "如果后面你又拿到了更新、更整理过的版本，就用那个真实输出替换这个文件。",
            "",
            raw_response.strip(),
            "",
        ]
    )


def build_case_manifest(found: dict[str, Path | None], manual_items: list[str]) -> str:
    lines = ["# 文件清单", "", "## 自动找到的文件", ""]
    for label, path in found.items():
        lines.append(f"- {label}: `{path if path else 'missing'}`")
    lines.extend(["", "## 需要人工后续补充的内容", ""])
    for item in manual_items:
        lines.append(f"- {item}")
    lines.append("")
    return "\n".join(lines)


def bundle_once(root: Path) -> None:
    prepare_root(root)

    scenario_json = SOURCE_SCENARIO_USED if SOURCE_SCENARIO_USED.exists() else PROJECT_ROOT / "processed/runnable_seeds/scenario-case_001.json"
    scenario_text = read_text(scenario_json)
    llm_input = read_json(SOURCE_LLM_INPUT)
    critical = read_json(SOURCE_CRITICAL_WINDOW)
    raw_response = read_text(SOURCE_LLM_OUTPUT) if SOURCE_LLM_OUTPUT.exists() else "TODO: paste the real webpage-model causal explanation here.\n"
    meta_text = read_text(SOURCE_META) if SOURCE_META.exists() else "TODO: actual local run command not auto-recovered.\n"
    error_json = read_json(SOURCE_ERROR) if SOURCE_ERROR.exists() else {}

    write_text(root / "00_README.md", build_readme())
    write_text(root / "01_case001_runnable_json/scenario-case_001.json", scenario_text)
    write_text(root / "01_case001_runnable_json/json_description.md", build_json_description())

    write_text(root / "02_execution_evidence/run_command.txt", meta_text.strip() + "\n")
    write_text(root / "02_execution_evidence/run_log_excerpt.txt", build_run_log_excerpt(meta_text, error_json, SOURCE_BAG))
    write_text(root / "02_execution_evidence/oracle_result_summary.md", build_oracle_summary(error_json, SOURCE_BAG))
    write_text(
        root / "02_execution_evidence/rosbag_path.txt",
        f"{SOURCE_BAG}\n" if SOURCE_BAG.exists() else "TODO: rosbag path not found.\n",
    )

    if SOURCE_BAG.exists():
        bag_info = "\n".join(
            [
                f"path: {SOURCE_BAG}",
                f"size_bytes: {SOURCE_BAG.stat().st_size}",
                f"size_gb: {SOURCE_BAG.stat().st_size / (1024**3):.3f}",
                "rosbag_info: `rosbag` command not available in the current environment; only path and size were recorded automatically.",
                "",
            ]
        )
    else:
        bag_info = "TODO: rosbag file not found.\n"
    write_text(root / "02_execution_evidence/rosbag_info.txt", bag_info)
    write_text(
        root / "02_execution_evidence/screenshots/TODO.md",
        "\n".join(
            [
                "# 截图 TODO",
                "",
                "- 当前可访问的文件快照里，没有自动找到执行截图。",
                "- 如果你手头有 CARLA / RViz / DriveFuzz 的真实运行截图，请把 2–3 张关键图片复制到这个目录。",
                "",
            ]
        ),
    )

    write_text(
        root / "03_llm_causal_explanation/input_scenario_data_plus_fault_label.md",
        build_input_scenario_markdown(llm_input, critical),
    )
    if SOURCE_PROMPT.exists():
        copy_if_exists(SOURCE_PROMPT, root / "03_llm_causal_explanation/prompt_template.md")
    else:
        write_text(root / "03_llm_causal_explanation/prompt_template.md", "TODO: copy the actual proposal_v2 prompt here.\n")
    write_text(root / "03_llm_causal_explanation/llm_output_example_or_TODO.md", build_llm_todo_or_output(raw_response))
    write_text(root / "03_llm_causal_explanation/root_cause_pattern_draft.md", extract_root_cause_draft(raw_response))

    write_text(root / "04_next_steps/next_experiment_plan.md", build_next_steps())

    copy_if_exists(PROJECT_ROOT / "scripts/package_case001_bundle.py", root / "scripts/package_case001_bundle.py")
    copy_if_exists(SOURCE_EXPORT_SCRIPT, root / "scripts/export_runnable_seed.py")
    write_text(
        root / "scripts/parse_execution_artifacts.py",
        "\n".join(
            [
                "#!/usr/bin/env python3",
                "from pathlib import Path",
                "",
                "error_json = Path('../02_execution_evidence').resolve().parent / '02_execution_evidence' / 'oracle_result_summary.md'",
                "print('当前这个 bundle 使用的是已保留的 meta 和 error JSON 执行产物，而不是重新独立跑了一次 parser。')",
                "print(f'请查看: {error_json}')",
                "",
            ]
        )
        + "\n",
    )

    found = {
        "scenario_json_used_on_disk": scenario_json,
        "seed_zip_from_wechat": SOURCE_SCENARIO_ZIP if SOURCE_SCENARIO_ZIP.exists() else None,
        "meta_command": SOURCE_META if SOURCE_META.exists() else None,
        "queue_json": SOURCE_QUEUE if SOURCE_QUEUE.exists() else None,
        "error_json": SOURCE_ERROR if SOURCE_ERROR.exists() else None,
        "rosbag": SOURCE_BAG if SOURCE_BAG.exists() else None,
        "proposal_v2_prompt": SOURCE_PROMPT if SOURCE_PROMPT.exists() else None,
        "saved_llm_output": SOURCE_LLM_OUTPUT if SOURCE_LLM_OUTPUT.exists() else None,
    }
    manual_items = [
        "如果你有真实执行截图，请把 2–3 张放到 `02_execution_evidence/screenshots/`。",
        "如果后面能进入 ROS 环境，请用完整 `rosbag info` 输出替换现在的 `rosbag_info.txt`。",
        "如果完整 console log 在别的目录，请用真实保存下来的关键行替换 `run_log_excerpt.txt`。",
    ]
    write_text(root / "file_manifest.md", build_case_manifest(found, manual_items))


def main() -> None:
    bundle_once(BUNDLE_ROOT)
    if EXTERNAL_ROOT.parent.exists():
        bundle_once(EXTERNAL_ROOT)
    else:
        print(f"External target missing: {EXTERNAL_ROOT.parent}")


if __name__ == "__main__":
    main()
