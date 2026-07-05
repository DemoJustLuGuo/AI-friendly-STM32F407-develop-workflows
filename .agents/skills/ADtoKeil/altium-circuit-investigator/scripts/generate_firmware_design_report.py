#!/usr/bin/env python3
"""Generate a Chinese firmware-design Markdown scaffold from Altium inventory."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from coverage_report import build_report
from port_inventory import pcb_inventory, schematic_inventory


def _mode_guess(pin: dict[str, Any]) -> str:
    net = str(pin.get("net", "")).upper()
    pin_name = str(pin.get("pin_name", "")).upper()
    text = f"{net} {pin_name}"
    if any(x in net for x in ("PUMP_AD", "_AD", "ADC", "NTC", "TEMP", "CUR", "VOLT", "LEVEL")):
        return "ADC / 待确认采样范围"
    if any(x in net for x in ("VSP", "PWM")):
        return "PWM 或 GPIO / 待拓扑确认"
    if any(x in net for x in ("FG", "TACH")):
        return "Timer capture / GPIO interrupt"
    if any(x in net for x in ("PUMP_CTRL", "CTRL", "OUT", "SW", "COMP", "RELAY", "LED", "QD_")):
        return "GPIO Output / 待确认有效电平"
    if any(x in net for x in ("KEY", "LEVEL", "SENSE", "DET")):
        return "GPIO Input 或 ADC / 待拓扑确认"
    if any(x in net for x in ("TX", "RX")):
        return "UART / 待确认协议"
    if any(x in net for x in ("SCL", "SDA")):
        return "I2C / 待确认上拉和从机"
    if any(x in net for x in ("VDD", "VCC", "GND", "+5V", "3V")):
        return "Power / not firmware GPIO"
    if any(x in pin_name for x in ("PWM", "AIN", "INT", "TX", "RX")):
        return "待确认 / MCU pin has alternate function"
    return "待确认"


def _md_escape(value: Any) -> str:
    return str(value if value is not None else "").replace("|", "\\|").replace("\n", " ")


def _all_mcu_pins(inventory: dict[str, Any]) -> list[dict[str, Any]]:
    pins: list[dict[str, Any]] = []
    seen: set[tuple[str, str, str]] = set()
    for mcu in inventory.get("mcu_like") or []:
        for pin in mcu.get("pins") or []:
            key = (
                str(pin.get("pin") or ""),
                str(pin.get("pin_name") or ""),
                str(pin.get("net") or ""),
            )
            if key in seen:
                continue
            seen.add(key)
            pins.append(pin)
    return sorted(pins, key=lambda p: str(p.get("pin") or ""))


def generate_markdown(inventory: dict[str, Any], coverage: dict[str, Any], title: str) -> str:
    summary = coverage["summary"]
    lines = [
        f"# {title}",
        "",
        "## 1. 资料来源和解析置信度",
        "",
        f"- 原理图：`{inventory.get('schdoc', '')}`",
        f"- PCB：`{inventory.get('pcbdoc', '未提供')}`",
        "- 说明：本报告是硬件证据驱动的固件设计起点；`待确认` 项需要结合局部截图、PCB、datasheet 或实测继续确认。",
        "",
        "## 2. 端口覆盖率摘要",
        "",
        "| 项目 | 数量 |",
        "| --- | --- |",
    ]
    for key, value in summary.items():
        if isinstance(value, dict):
            value = ", ".join(f"{k}: {v}" for k, v in sorted(value.items()))
        lines.append(f"| {key} | {_md_escape(value)} |")

    lines += [
        "",
        "## 3. MCU 引脚逐项确认表",
        "",
        "| Pin | Pin name | Net | 初步固件模式 | 证据 | 安全态/极性 | 待确认 |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for pin in _all_mcu_pins(inventory):
        evidence = f"netlist: MCU pin {pin.get('pin')} -> {pin.get('net')}"
        lines.append(
            "| {pin} | {pin_name} | {net} | {mode} | {evidence} | 待确认 | 需要 trace_net_deep / 局部截图 / datasheet |".format(
                pin=_md_escape(pin.get("pin")),
                pin_name=_md_escape(pin.get("pin_name")),
                net=_md_escape(pin.get("net")),
                mode=_md_escape(_mode_guess(pin)),
                evidence=_md_escape(evidence),
            )
        )

    lines += [
        "",
        "## 4. 外部连接器/端子功能确认表",
        "",
        "| Connector | Pin | Net | 证据 | 推测外设 | 固件责任 | 测试方法 |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for conn in inventory.get("connectors") or []:
        for pin in conn.get("pins") or []:
            lines.append(
                "| {conn} | {pin} | {net} | netlist: {conn} pin {pin} | 待确认 | 待确认 | 万用表/示波器/线束定义确认 |".format(
                    conn=_md_escape(conn.get("designator")),
                    pin=_md_escape(pin.get("pin")),
                    net=_md_escape(pin.get("net")),
                )
            )

    lines += [
        "",
        "## 5. 可疑网络优先追踪清单",
        "",
        "| Net | Terminals | 追踪建议 |",
        "| --- | --- | --- |",
    ]
    for net in coverage.get("suspicious_nets_for_review") or []:
        lines.append(
            f"| {_md_escape(net.get('name'))} | {_md_escape(net.get('terminal_count'))} | trace_net_deep + render_region + PCB 端点确认 |"
        )

    lines += [
        "",
        "## 6. MCU 外设资源分配",
        "",
        "| 外设 | 信号/网络 | 用途 | 配置要点 | 待确认 |",
        "| --- | --- | --- | --- | --- |",
        "| GPIO Output | 待填 | 继电器/泵/电机/电源使能等 | 上电安全态、有效电平、超时保护 | 由拓扑确认 |",
        "| GPIO Input | 待填 | 按键/水位/保护输入等 | 上拉下拉、消抖、异常态 | 由连接器和滤波确认 |",
        "| ADC | 待填 | 温度/电压/电流/模拟量 | 采样周期、滤波、开短路阈值 | 由分压和传感器确认 |",
        "| PWM/Timer | 待填 | 风机/电机/VSP/FG 等 | 频率、占空比、捕获滤波 | 由拓扑和 datasheet 确认 |",
        "| UART/I2C/SPI | 待填 | 通信/显示/传感器 | 波特率/地址/上拉/电平 | 由连接器和芯片确认 |",
        "",
        "## 7. 上电初始化和安全态",
        "",
        "1. 初始化所有输出为硬件安全态。",
        "2. 读取输入和 ADC 原始值，只记录不动作。",
        "3. 检查电源、复位、通信、关键传感器是否正常。",
        "4. 按低风险到高风险顺序开启输出。",
        "5. 每个执行器动作必须带超时和反馈/电流/状态检查。",
        "",
        "## 8. 控制状态机",
        "",
        "| 状态 | 进入条件 | 输出动作 | 反馈检查 | 退出/故障 |",
        "| --- | --- | --- | --- | --- |",
        "| INIT | 上电/复位 | 所有执行器安全态 | 电源和输入自检 | 进入 IDLE 或 FAULT |",
        "| IDLE | 自检通过 | 等待命令/条件 | 周期采样 | 进入 RUN 或 FAULT |",
        "| RUN | 控制条件满足 | 按功能开启执行器 | 反馈闭环/超时 | 进入 IDLE 或 FAULT |",
        "| FAULT | 检测到异常 | 关闭危险输出 | 锁存故障码 | 人工/条件恢复 |",
        "",
        "## 9. 故障保护和恢复策略",
        "",
        "| 故障 | 检测来源 | 判定条件 | 软件动作 | 恢复条件 |",
        "| --- | --- | --- | --- | --- |",
        "| 传感器开路/短路 | ADC/GPIO | 超出有效范围 | 关闭相关输出，记录故障 | 恢复正常并满足延时 |",
        "| 执行器无反馈 | FG/电流/状态输入 | 动作后超时未变化 | 停止输出，重试或锁故障 | 人工/自动策略待定 |",
        "| 通信异常 | UART/I2C/SPI | 超时/CRC/无响应 | 降级或停机 | 通信恢复 |",
        "",
        "## 10. 调试命令和量产测试",
        "",
        "- `pin_dump`：打印所有 GPIO/ADC/Timer 原始值，按网络名显示。",
        "- `out_test <net> <on/off>`：带安全超时的单路输出测试。",
        "- `adc_log <channel>`：输出原始值、滤波值、最大/最小值。",
        "- `freq_log <net>`：输出 FG/tach 捕获频率。",
        "- `factory_test`：按安全顺序执行输出并检查反馈。",
        "",
        "## 11. 确认 / 推测 / 待确认问题清单",
        "",
        "| 项目 | 状态 | 下一步证据 |",
        "| --- | --- | --- |",
        "| 每个 MCU pin 功能 | 待逐项确认 | trace_net_deep、局部截图、datasheet |",
        "| 每个连接器外部设备 | 待逐项确认 | PCB 丝印、线束定义、实物测量 |",
        "| 每个执行器有效电平 | 待逐项确认 | 拓扑方向、示波器、负载测试 |",
        "",
    ]
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--schdoc", type=Path, required=True)
    parser.add_argument("--pcbdoc", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--title", default="基于原理图和 PCB 的嵌入式软件设计")
    args = parser.parse_args()

    inventory = schematic_inventory(args.schdoc)
    if args.pcbdoc:
        inventory.update(pcb_inventory(args.pcbdoc))
    coverage = build_report(inventory)
    args.out.write_text(generate_markdown(inventory, coverage, args.title), encoding="utf-8")
    sidecar = args.out.with_suffix(".inventory.json")
    sidecar.write_text(json.dumps(inventory, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
