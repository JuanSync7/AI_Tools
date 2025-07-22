#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# lint_sv_blocks.py: Enhanced SystemVerilog linter with flexible input options

#===============================================================================
# SECTION 1: GLOBAL VARIABLES & ISSUE CATEGORIES
# SECTION 2: ISSUE ADDING FUNCTIONS
# SECTION 3: LLM PROMPT GENERATION
# SECTION 4: HELP MESSAGE DOCUMENTATION
# SECTION 5: COMMAND LINE ARGUMENT PARSING
# SECTION 6: FILE COLLECTION LOGIC
# SECTION 7: MAIN LINT CHECK IMPLEMENTATIONS
# SECTION 8: FINAL REPORTING AND OUTPUT
#===============================================================================

#===============================================================================
# MAINTAINER'S GUIDE - ADDING NEW LINT CHECKS
#===============================================================================
#
# This script follows a structured architecture for scalable maintenance.
# When adding new lint checks, you MUST update ALL the following sections
# to maintain completeness and quality.
#
# SCRIPT ARCHITECTURE OVERVIEW:
# 1. Global Variables & Issue Categories (lines ~80-90)
# 2. Issue Adding Functions (lines ~95-140)
# 3. Help Message Documentation (lines ~500-700)
# 4. File Collection Logic (lines ~750-820)
# 5. Lint Check Implementation (lines ~830-1150)
# 6. LLM Prompt Generation (lines ~145-490)
#
#===============================================================================
# STEP-BY-STEP GUIDE TO ADD A NEW LINT CHECK:
#===============================================================================
#
# STEP 1: DETERMINE ISSUE CATEGORY
# --------------------------------
# Categorize your new check into one of these categories:
#   • critical_issues       - Blocks compilation/simulation (timescale, syntax)
#   • style_issues          - Coding standards (formatting, naming)
#   • best_practice_issues  - Code quality (documentation, robustness)
#   • performance_issues    - Synthesis/timing (assignment types, optimization)
#
# STEP 2: UPDATE HELP MESSAGE (REQUIRED)
# --------------------------------------
# Location: create_arg_parser() function's epilog (lines ~520-550)
# Add your new check to the appropriate category section:
#   🚨 CRITICAL ISSUES, 🎨 STYLE ISSUES, ⚡ PERFORMANCE ISSUES, 📋 BEST PRACTICE
# Format: "✓ Your new check description → Benefit/reason"
# Example: "✓ Missing parameter declarations → Prevents compilation errors"
#
# STEP 3: IMPLEMENT THE CHECK LOGIC (REQUIRED)
# --------------------------------------------
# Location: Main checking section (lines ~830-1150)
# Create a new function for your check and add it to the `main()` function call list.
#
# def check_my_new_issue(sv_files):
#     logging.info("Checking for [your check description]...")
#     issue_variable = []
#     for f in sv_files:
#         try:
#             with open(f, 'r', encoding='utf-8') as file:
#                 for line_num, line in enumerate(file, 1):
#                     if re.search(r'your_pattern', line):
#                         issue_variable.append(f"{f}:{line_num}: {line.strip()}")
#         except IOError as e:
#             logging.warning(f"Could not read file {f}: {e}")
#
#     if issue_variable:
#         add_[category]_issue("Issue Title", "\n".join(issue_variable), "Solution description")
#
# STEP 4: ADD TO LLM PROMPT EXAMPLES (RECOMMENDED)
# ------------------------------------------------
# Location: generate_llm_prompt() function (lines ~240-400)
# Find the appropriate category section and add code examples:
#   if "your check keyword" in title:
#       llm_prompt += """**Example Fix:**
# ```systemverilog
# // ❌ Before: Problem description
# [problematic code example]
#
# // ✅ After: Improved code
# [corrected code example]
# ```
# """
#
# STEP 5: UPDATE VARIABLE DECLARATIONS (IF NEEDED)
# ------------------------------------------------
# Location: Top of script (lines ~80-90)
# If adding a new category, declare the dictionary:
# your_new_category_issues = {}
#
# And add the corresponding function (lines ~95-140):
# def add_your_new_category_issue(title, content, solution):
#     global fail, total_issues
#     if content:
#         fail = True
#         your_new_category_issues[title] = {"content": content, "solution": solution}
#         total_issues += 1
#
# STEP 6: UPDATE LLM PROMPT GENERATION (IF NEW CATEGORY)
# ------------------------------------------------------
# Location: generate_llm_prompt() function
# Add a new section for your category following the existing pattern.
#
#===============================================================================
# VERSION HISTORY & CHANGE LOG
#===============================================================================
#
# Version 2.1.0 | 2024-01-15 | John Smith
# ------------------------------------------
# [ADDED]   New check for missing parameter validation in modules
# [ADDED]   Detection of unused variable declarations
# [CHANGED] Enhanced LLM prompt with more detailed code examples
# [FIXED]   False positive in always block comment detection
#
# Version 2.0.0 | 2024-01-01 | Jane Doe
# ------------------------------------------
# [ADDED]   Complete maintainer's guide with step-by-step instructions
# [ADDED]   Section markers for easy navigation
# [CHANGED] Restructured script architecture for better scalability
# [ADDED]   Comprehensive help message with usage examples
#
#===============================================================================

"""
lint_sv_blocks.py

A professional SystemVerilog linter for RTL codebases, designed for maintainability, synthesis, and verification compliance.

Key features:
- Detects critical, style, best practice, and performance issues in SystemVerilog files.
- Supports flexible input: single files, directories, or filelists.
- Generates a comprehensive LLM prompt for code review and automated fixing.
- Provides detailed, categorized output and actionable guidance for code improvement.

Basic usage:
    ./lint_sv_blocks.py rtl/
    ./lint_sv_blocks.py myfile.sv
    ./lint_sv_blocks.py -f filelist.f

See the help message for advanced options and integration tips.
"""

import argparse
import logging
import os
import re
import sys
from pathlib import Path

#===============================================================================
# SECTION 1: GLOBAL VARIABLES & ISSUE CATEGORIES
#===============================================================================
# Add new issue categories here if needed (see STEP 5 in maintainer's guide)

fail: bool = False
total_issues: int = 0

# Issue categories - ADD NEW CATEGORIES HERE IF NEEDED
critical_issues: dict = {}
style_issues: dict = {}
best_practice_issues: dict = {}
performance_issues: dict = {}

# Color output for better visibility
class Colors:
    """ANSI color codes for terminal output."""
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    NC = '\033[0m' # No Color


def remove_ansi_codes(text: str) -> str:
    """
    Removes ANSI escape codes from a string.

    Args:
        text (str): The string potentially containing ANSI codes.

    Returns:
        str: The string with ANSI codes removed.
    """
    ansi_escape = re.compile(r'\x1B\[[0-?]*[ -/]*[@-~]')
    return ansi_escape.sub('', text)

class PlainFormatter(logging.Formatter):
    """
    Custom formatter that strips ANSI color codes for file logging.
    """
    def format(self, record):
        message = super().format(record)
        return remove_ansi_codes(message)

#===============================================================================
# SECTION 2: ISSUE ADDING FUNCTIONS
#===============================================================================
# Add new issue category functions here if needed (see STEP 5 in maintainer's guide)

def add_critical_issue(title: str, content: str, solution: str) -> None:
    """
    Adds a critical issue to the global dictionary.

    Args:
        title (str): The issue title/category.
        content (str): The details or locations of the issue.
        solution (str): The recommended solution or fix.

    Returns:
        None
    """
    global fail, total_issues
    if content:
        fail = True
        if title not in critical_issues:
            critical_issues[title] = {"content": content, "solution": solution}
            total_issues += 1
        else: # Append content if title already exists
            critical_issues[title]["content"] += "\n" + content


def add_style_issue(title: str, content: str, solution: str) -> None:
    """
    Adds a style issue to the global dictionary.

    Args:
        title (str): The issue title/category.
        content (str): The details or locations of the issue.
        solution (str): The recommended solution or fix.

    Returns:
        None
    """
    global fail, total_issues
    if content:
        fail = True
        if title not in style_issues:
            style_issues[title] = {"content": content, "solution": solution}
            total_issues += 1
        else:
            style_issues[title]["content"] += "\n" + content


def add_best_practice_issue(title: str, content: str, solution: str) -> None:
    """
    Adds a best practice issue to the global dictionary.

    Args:
        title (str): The issue title/category.
        content (str): The details or locations of the issue.
        solution (str): The recommended solution or fix.

    Returns:
        None
    """
    global fail, total_issues
    if content:
        fail = True
        if title not in best_practice_issues:
            best_practice_issues[title] = {"content": content, "solution": solution}
            total_issues += 1
        else:
            best_practice_issues[title]["content"] += "\n" + content


def add_performance_issue(title: str, content: str, solution: str) -> None:
    """
    Adds a performance issue to the global dictionary.

    Args:
        title (str): The issue title/category.
        content (str): The details or locations of the issue.
        solution (str): The recommended solution or fix.

    Returns:
        None
    """
    global fail, total_issues
    if content:
        fail = True
        if title not in performance_issues:
            performance_issues[title] = {"content": content, "solution": solution}
            total_issues += 1
        else:
            performance_issues[title]["content"] += "\n" + content

#===============================================================================
# SECTION 3: LLM PROMPT GENERATION
#===============================================================================
# Add new category sections here if adding new issue categories (see STEP 6 in maintainer's guide)
# Add new code examples in existing category sections (see STEP 4 in maintainer's guide)

def generate_llm_prompt(sv_files: list[str]) -> str:
    """
    Generate a comprehensive LLM prompt summarizing all linting issues found.

    Args:
        sv_files (list[str]): List of SystemVerilog file paths that were checked.

    Returns:
        str: The formatted LLM prompt string for code review and fixing.
    """
    files_with_issues = set()
    all_issues = [critical_issues, style_issues, best_practice_issues, performance_issues]
    for category in all_issues:
        for title in category:
            content = category[title]["content"]
            for line in content.split('\n'):
                if line:
                    files_with_issues.add(line.split(':')[0])

    llm_prompt = f"""# SystemVerilog Linting Issues

## PROJECT CONTEXT
You are a Senior RTL Engineer with 10+ years of experience. You are working on a Systemverilog RTL Project.
You are following strict SystemVerilog coding standards for maintainability, synthesis, and verification.
Below are the files that need to be linted after running a lint check. Please fix the issues and provide a detailed explanation of the changes you made.

## GOAL - Success Criteria and Objectives
Achieve a **100% lint-clean SystemVerilog codebase** that:
- ✅ Compiles without errors in all EDA tools
- ✅ Follows consistent coding standards for team collaboration
- ✅ Meets synthesis and timing closure requirements
- ✅ Passes automated quality checks and code reviews
- ✅ Is maintainable and well-documented

## BEFORE/AFTER - Current vs Desired State
**BEFORE (Current State):**
- {len(sv_files)} files with {total_issues} categories of lint violations
- Compilation/simulation blockers present
- Inconsistent coding style and formatting
- Missing documentation and best practices

**AFTER (Desired State):**
- Zero lint violations across all SystemVerilog files
- Clean compilation and simulation
- Professional-grade code following industry standards
- Comprehensive documentation and comments

## RESULT - Expected Outcomes and Deliverables
**Upon completion, you must provide:**
1. **Modified SystemVerilog files** with all issues resolved
2. **Summary of changes** made per file with explanations
3. **Verification confirmation** that functionality is preserved
4. **Quality improvement metrics** showing before/after status

## FORMAT - How to Structure the Output/Response
**Required response structure:**
```
## EXECUTIVE SUMMARY
- Files Modified: [count]
- Issues Resolved: [count by category]
- Compilation Status: [PASS/FAIL]

## DETAILED CHANGES
### [FileName.sv]
**Issues Fixed:**
- [Issue type]: [description of fix]

**Code Changes:**
```systemverilog
// Before:
[original code]

// After:
[corrected code]
```

## LINTING SUMMARY
- **Total Files Checked:** {len(sv_files)}
- **Total Issue Categories:** {total_issues}
- **Files with Issues:** {len(files_with_issues)}

"""

    # Critical Issues
    if critical_issues:
        llm_prompt += "## 🚨 CRITICAL ISSUES (Fix First - Blocks Compilation/Simulation)\n\n"
        for i, (title, data) in enumerate(critical_issues.items(), 1):
            llm_prompt += f"### {i}. {title}\n\n"
            llm_prompt += f"**Issue:** {data['solution']}\n\n"
            llm_prompt += f"**Affected Files/Lines:**\n```\n{data['content']}\n```\n\n"
            llm_prompt += "**Action Required:** Fix these issues immediately as they prevent compilation or simulation.\n\n"

    # Style Issues
    if style_issues:
        llm_prompt += "## 🎨 STYLE ISSUES (Coding Standard Violations)\n\n"
        for i, (title, data) in enumerate(style_issues.items(), 1):
            llm_prompt += f"### {i}. {title}\n\n"
            llm_prompt += f"**Issue:** {data['solution']}\n\n"
            llm_prompt += f"**Affected Files/Lines:**\n```\n{data['content']}\n```\n\n"
            # Add code examples for common style issues - ADD NEW EXAMPLES HERE (STEP 4)
            if "C-style curly braces" in title:
                llm_prompt += """**Example Fix:**
```systemverilog
// ❌ Incorrect (C-style)
if (condition) {
    signal <= value;
}

// ✅ Correct (SystemVerilog style)
if (condition) begin
    signal <= value;
end
```

"""
            elif "Tabs detected" in title:
                llm_prompt += "**Fix:** Replace all tabs with 4 spaces. Use your editor's \"Convert Tabs to Spaces\" function.\n\n"
            elif "Lines longer than 120" in title:
                llm_prompt += """**Example Fix:**
```systemverilog
// ❌ Too long
assign very_long_signal_name = (condition1 && condition2 && condition3) ? long_value_name : another_long_value_name;

// ✅ Properly broken
assign very_long_signal_name = (condition1 && condition2 && condition3) ?
                               long_value_name :
                               another_long_value_name;
```

"""
            elif "Multiple ports per line" in title:
                llm_prompt += """**Example Fix:**
```systemverilog
// ❌ Multiple ports per line
input logic clk, rst_n;
output logic x, y;

// ✅ One port per line
input logic clk;
input logic rst_n;
output logic x;
output logic y;
```

"""

    # Best Practice Issues
    if best_practice_issues:
        llm_prompt += "## 📋 BEST PRACTICE ISSUES (Improve Code Quality)\n\n"
        for i, (title, data) in enumerate(best_practice_issues.items(), 1):
            llm_prompt += f"### {i}. {title}\n\n"
            llm_prompt += f"**Issue:** {data['solution']}\n\n"
            llm_prompt += f"**Affected Files/Lines:**\n```\n{data['content']}\n```\n\n"
            if "missing default cases" in title:
                llm_prompt += """**Example Fix:**
```systemverilog
// ❌ Missing default
case (opcode)
    3'b000: result = a + b;
    3'b001: result = a - b;
endcase

// ✅ With default
case (opcode)
    3'b000: result = a + b;
    3'b001: result = a - b;
    default: result = '0;  // or appropriate default
endcase
```

"""
            elif "Missing comments before always" in title:
                llm_prompt += """**Example Fix:**
```systemverilog
// ❌ No comment
always_ff @(posedge clk) begin
    if (reset) counter <= '0;
    else counter <= counter + 1;
end

// ✅ With descriptive comment
// Counter logic: Increment on each clock cycle, reset to 0 on reset
always_ff @(posedge clk) begin
    if (reset) counter <= '0;
    else counter <= counter + 1;
end
```

"""
            elif "Unnamed generate blocks" in title:
                llm_prompt += """**Example Fix:**
```systemverilog
// ❌ Unnamed generate block
generate
    for (genvar i = 0; i < 4; i++) begin
        // ...
    end
endgenerate

// ✅ Named generate block
generate
    for (genvar i = 0; i < 4; i++) begin : gen_label
        // ...
    end
endgenerate
```

"""
            elif "Unguarded initial block" in title:
                llm_prompt += """**Example Fix:**
```systemverilog
// ❌ Unguarded initial block
initial begin
    // simulation-only code
end

// ✅ Guarded initial block
`ifndef SYNTHESIS
initial begin
    // simulation-only code
end
`endif
```

"""

    # Performance Issues
    if performance_issues:
        llm_prompt += "## ⚡ PERFORMANCE ISSUES (Synthesis/Timing Concerns)\n\n"
        for i, (title, data) in enumerate(performance_issues.items(), 1):
            llm_prompt += f"### {i}. {title}\n\n"
            llm_prompt += f"**Issue:** {data['solution']}\n\n"
            llm_prompt += f"**Affected Files/Lines:**\n```\n{data['content']}\n```\n\n"
            if "blocking assignments in clocked" in title:
                llm_prompt += """**Example Fix:**
```systemverilog
// ❌ Blocking assignment in clocked logic (can cause race conditions)
always_ff @(posedge clk) begin
    temp = input_data;     // Bad: blocking assignment
    output_reg = temp + 1; // Bad: blocking assignment
end

// ✅ Non-blocking assignments in clocked logic
always_ff @(posedge clk) begin
    temp <= input_data;    // Good: non-blocking
    output_reg <= temp + 1; // Good: non-blocking
end
```

"""
            elif "non-blocking assignments in combinational" in title:
                llm_prompt += """**Example Fix:**
```systemverilog
// ❌ Non-blocking in combinational logic
always_comb begin
    temp <= a + b;   // Bad: non-blocking in combinational
    result <= temp;  // Bad: creates delta delay issues
end

// ✅ Blocking assignments in combinational logic
always_comb begin
    temp = a + b;    // Good: blocking assignment
    result = temp;   // Good: immediate assignment
end
```

"""

    # Prioritized Action Plan
    llm_prompt += "## 📝 PRIORITIZED ACTION PLAN\n\n"
    llm_prompt += "### Phase 1: Critical Fixes (Do First)\n"
    if not critical_issues:
        llm_prompt += "- [x] No critical issues found ✅\n"
    else:
        for title in critical_issues:
            llm_prompt += f"- [ ] Fix: {title}\n"

    llm_prompt += "\n### Phase 2: Style Consistency\n"
    if not style_issues:
        llm_prompt += "- [x] No style issues found ✅\n"
    else:
        for title in style_issues:
            llm_prompt += f"- [ ] Fix: {title}\n"

    llm_prompt += "\n### Phase 3: Best Practices & Performance\n"
    phase3_tasks = list(best_practice_issues.keys()) + list(performance_issues.keys())
    if not phase3_tasks:
        llm_prompt += "- [x] No best practice or performance issues found ✅\n"
    else:
        for title in best_practice_issues:
            llm_prompt += f"- [ ] Improve: {title}\n"
        for title in performance_issues:
            llm_prompt += f"- [ ] Optimize: {title}\n"

    # Implementation Guidance
    llm_prompt += """
## 🎯 IMPLEMENTATION GUIDANCE

### File Header Template
Each SystemVerilog file should start with:
```systemverilog
//=============================================================================
// Company: <Company Name>
// Project Name: <ProjectName>
//
// File: <FileName.sv>
//
// ----- Fields for Automated Documentation -----
// MODULE_NAME: <ModuleName>
// AUTHOR: <Author Name> (<author_email@company.com>)
// VERSION: <X.Y.Z>
// DATE: <YYYY-MM-DD>
// DESCRIPTION: <Brief, description of the module's purpose.>
// PRIMARY_PURPOSE: <Detailed purpose of the module.>
// ROLE_IN_SYSTEM: <How this module fits into a larger system.>
// PROBLEM_SOLVED: <What specific problem this module addresses.>
// MODULE_TYPE: <e.g., RTL, Behavioral, Testbench_Component>
// TARGET_TECHNOLOGY_PREF: <ASIC/FPGA>
// RELATED_SPECIFICATION: <Document_Name_Or_Link_to_Spec>
//
// ----- Status and Tracking -----
// VERIFICATION_STATUS: <Not Verified | In Progress | Verified | Formally Verified>
// QUALITY_STATUS: <Draft | Reviewed | Approved | Released>
//
//=============================================================================

`timescale 1ns/1ps
`default_nettype none
```

### File Footer Template
Each SystemVerilog file should end with:
```systemverilog
  //=============================================================================
  // Dependencies: <list of dependencies>
  //
  // Instantiated In:
  //   - core/integration/some_subsystem.sv
  //   - memory/controller/another_module.sv
  //
  // Performance:
  //   - Critical Path: <expected critical path>
  //   - Max Frequency: <range of frequency>
  //   - Area: <rough estimate>
  //
  // Verification Coverage:
  //   - Code Coverage: <Coverage from tool>
  //   - Functional Coverage: <Coverage from tool>
  //   - Branch Coverage: <Coverage from tool>
  //
  // Synthesis:
  //   - Target Technology: ASIC/FPGA
  //   - Synthesis Tool: Design Compiler/Quartus
  //   - Clock Domains: <number of clk domain>
  //   - Constraints File: <SDC file name>
  //
  // Testing:
  //   - Testbench: <testbench name>
  //   - Test Vectors: <number of test vectors in testbench mentioned above>
  //
  //----
  // Revision History:
  // Version | Date       | Author            | Description
  //=============================================================================
  // 1.1.0   |kloudformation-MM-DD | <Author Name>     | Added X / Implemented Y (Summary of changes)
  // 1.0.0   |kloudformation-MM-DD | <Author Name>     | Initial release
  //=============================================================================
```

### Coding Standards Summary
- **Indentation:** 4 spaces, no tabs
- **Line Length:** Maximum 120 characters
- **Block Style:** SystemVerilog `begin/end`, not C-style `{}`
- **Clocked Logic:** Use non-blocking assignments (`<=`)
- **Combinational Logic:** Use blocking assignments (`=`)
- **Comments:** Describe purpose before every `always` block
- **Case Statements:** Always include `default` clause
- **Generate Blocks:** Always use labels (`begin : label_name`)

### Next Steps
1. **Run the fixes** in the order specified (Critical → Style → Best Practices)
2. **Test compilation** after each phase to catch any new issues
3. **Run the linter again** to verify all issues are resolved
4. **Consider adding** additional verification testbenches for modified modules

---
**Note:** This analysis was performed on """
    llm_prompt += f"{len(sv_files)} SystemVerilog files. Focus on critical issues first to ensure the design compiles and simulates correctly.\n"

    return llm_prompt

#===============================================================================
# SECTION 4: HELP MESSAGE DOCUMENTATION
#===============================================================================
# Add new lint checks to appropriate category here (see STEP 2 in maintainer's guide)

def create_arg_parser() -> argparse.ArgumentParser:
    """
    Creates and returns the command-line argument parser for the linter.

    Returns:
        argparse.ArgumentParser: Configured argument parser for CLI options.
    """
    parser = argparse.ArgumentParser(
        description="SystemVerilog RTL Linter - Professional Code Quality Analyzer",
        formatter_class=argparse.RawTextHelpFormatter,
        epilog="""
═══════════════════════════════════════════════════════════════════════════════════
  COMPREHENSIVE CHECKS PERFORMED
═══════════════════════════════════════════════════════════════════════════════════

🚨 CRITICAL ISSUES (Compilation Blockers):
    ✓ Missing `timescale directive               → Simulation compatibility
    ✓ Missing `default_nettype none            → Prevents implicit wires
    ✓ Unbalanced begin/end blocks               → Compilation errors
    ✓ Syntax errors and malformed constructs    → Tool compatibility

🎨 STYLE ISSUES (Coding Standards):
    ✓ C-style braces {} vs SystemVerilog begin/end → Industry standards
    ✓ Tab characters vs consistent 4-space indent   → Team collaboration
    ✓ Lines exceeding 120 characters              → Code review readability
    ✓ Trailing whitespace on lines                → Clean version control
    ✓ Windows CRLF vs Unix LF line endings        → Cross-platform compatibility
    ✓ casez/casex vs explicit case statements   → Synthesis optimization
    ✓ Multiple ports per line in module header     → Readability and maintainability

⚡ PERFORMANCE ISSUES (Synthesis & Timing):
    ✓ Blocking assignments in clocked logic       → Race condition prevention
    ✓ Non-blocking assignments in combinational   → Simulation accuracy
    ✓ Assignment type mismatches                  → Synthesis warnings

📋 BEST PRACTICE ISSUES (Code Quality):
    ✓ Missing file headers and footers            → Documentation standards
    ✓ Missing default cases in case statements    → Robustness
    ✓ Multiple modules per file                   → Organization
    ✓ Files without comments                      → Maintainability
    ✓ Non-ANSI module declarations                → Modern SystemVerilog
    ✓ Unnamed generate blocks (context-aware)     → Debugging support
    ✓ Missing comments before always blocks       → Code clarity
    ✓ Unguarded initial blocks                  → Prevents accidental synthesis of simulation-only code

═══════════════════════════════════════════════════════════════════════════════════
  EXAMPLE USAGE SCENARIOS
═══════════════════════════════════════════════════════════════════════════════════

Basic Usage:
    ./lint_sv_blocks.py                           # Lint entire rtl/ directory
    ./lint_sv_blocks.py core/cpu.sv               # Lint single file
    ./lint_sv_blocks.py rtl/ memory/              # Lint multiple directories

Advanced Usage:
    ./lint_sv_blocks.py --no-recursive rtl/       # Non-recursive (rtl/ only)
    ./lint_sv_blocks.py -f project_files.f        # Use filelist
    ./lint_sv_blocks.py -f sim.f -f syn.f rtl/    # Multiple filelists + directory

CI/CD Integration:
    # Return code 0 = clean, 1 = issues found (suitable for automated flows)
    ./lint_sv_blocks.py && echo "PASS: Code quality check" || echo "FAIL: Fix issues"
"""
    )

    parser.add_argument(
        'targets',
        nargs='*',
        default=['rtl/'],
        help="""
TARGETS (Multiple inputs supported):
  Single File:            lint_sv_blocks.py myfile.sv
  Multiple Files:         lint_sv_blocks.py file1.sv file2.sv file3.sv
  Single Directory:       lint_sv_blocks.py rtl/
  Multiple Directories:   lint_sv_blocks.py rtl/ core/ memory/
  Mixed Inputs:           lint_sv_blocks.py rtl/ myfile.sv core/
"""
    )

    parser.add_argument(
        '-r', '--recursive',
        action='store_true',
        default=True,
        help="Search directories recursively (default: enabled)"
    )

    parser.add_argument(
        '-nr', '--no-recursive',
        action='store_false',
        dest='recursive',
        help="Search directories non-recursively (current level only)"
    )

    parser.add_argument(
        '-f', '--filelist',
        action='append',
        dest='filelists',
        default=[],
        metavar='FILE',
        help="Read file paths from filelist (one file path per line)"
    )
    
    parser.add_argument(
        '-I', '--interactive',
        action='store_true',
        help="Enable interactive mode to print logs to the console."
    )
    parser.add_argument(
        '--fix',
        action='store_true',
        help="Automatically fix trailing whitespace and Windows line endings in-place before linting."
    )
    return parser


def setup_logging(interactive_mode: bool) -> None:
    """
    Configures the logging system for file and (optionally) console output.

    Args:
        interactive_mode (bool): If True, also logs to the console.

    Returns:
        None
    """
    log_level = logging.INFO
    
    # Create logger
    logger = logging.getLogger()
    logger.setLevel(log_level)
    
    # Clear existing handlers
    if logger.hasHandlers():
        logger.handlers.clear()

    # File handler - always logs to a file
    file_handler = logging.FileHandler('lint_sv_blocks.log', mode='w')
    file_formatter = PlainFormatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)

    # Console handler - only logs to console if in interactive mode
    if interactive_mode:
        console_handler = logging.StreamHandler(sys.stdout)
        # Use a simpler formatter for the console to mimic original print behavior
        console_formatter = logging.Formatter('%(message)s')
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)

#===============================================================================
# SECTION 6: FILE COLLECTION LOGIC
#===============================================================================
# Generally no changes needed here unless modifying file discovery behavior

def collect_sv_files(targets: list[str], filelists: list[str], recursive: bool) -> list[str]:
    """
    Collects all .sv files from the provided targets and filelists.

    Args:
        targets (list[str]): List of file or directory paths to search.
        filelists (list[str]): List of filelist files (each line is a file path).
        recursive (bool): Whether to search directories recursively.

    Returns:
        list[str]: Sorted list of absolute paths to all found .sv files.
    """
    files = set()

    # Process filelists
    for filelist_path in filelists:
        if not os.path.isfile(filelist_path):
            logging.warning(f"{Colors.YELLOW}WARNING: Filelist '{filelist_path}' not found{Colors.NC}")
            continue
        with open(filelist_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    if os.path.isfile(line) and line.endswith('.sv'):
                        files.add(os.path.abspath(line))
                    elif os.path.isfile(line):
                         logging.warning(f"{Colors.YELLOW}WARNING: '{line}' from filelist is not a .sv file{Colors.NC}")
                    else:
                        logging.warning(f"{Colors.YELLOW}WARNING: '{line}' from filelist does not exist{Colors.NC}")

    # Process targets
    for target in targets:
        target_path = Path(target)
        if not target_path.exists():
            logging.warning(f"{Colors.YELLOW}WARNING: '{target}' does not exist{Colors.NC}")
            continue

        if target_path.is_file():
            if target.endswith('.sv'):
                files.add(os.path.abspath(target))
            else:
                logging.warning(f"{Colors.YELLOW}WARNING: '{target}' is not a .sv file{Colors.NC}")
        elif target_path.is_dir():
            if recursive:
                for sv_file in target_path.rglob('*.sv'):
                    files.add(os.path.abspath(sv_file))
            else:
                for sv_file in target_path.glob('*.sv'):
                    files.add(os.path.abspath(sv_file))

    return sorted(list(files))

#===============================================================================
# SECTION 7: MAIN LINT CHECK IMPLEMENTATIONS
#===============================================================================
# ADD NEW LINT CHECKS HERE (see STEP 3 in maintainer's guide)

def check_c_style_braces(sv_files: list[str]) -> None:
    """
    Checks for C-style braces in SystemVerilog files.

    Args:
        sv_files (list[str]): List of SystemVerilog file paths to check.

    Returns:
        None
    """
    logging.info("Checking for C-style braces...")
    issues = []
    # Regex to find C-style braces after common constructs, ignoring those inside comments
    pattern = re.compile(r"^(?!\s*//).*\b(if|else|for|while|case|always|initial)\b.*\{")
    for f in sv_files:
        try:
            with open(f, 'r', encoding='utf-8', errors='ignore') as file:
                for i, line in enumerate(file, 1):
                    if pattern.search(line):
                        issues.append(f"{f}:{i}: {line.strip()}")
        except IOError as e:
            logging.warning(f"Could not read file {f}: {e}")
    if issues:
        add_style_issue("C-style curly braces detected", "\n".join(issues), "Convert C-style braces {} to SystemVerilog begin/end blocks")

def check_tabs(sv_files: list[str]) -> None:
    """
    Checks for tabs in SystemVerilog files.

    Args:
        sv_files (list[str]): List of SystemVerilog file paths to check.

    Returns:
        None
    """
    logging.info("Checking for tabs...")
    issues = []
    for f in sv_files:
        try:
            with open(f, 'r', encoding='utf-8', errors='ignore') as file:
                for i, line in enumerate(file, 1):
                    if '\t' in line:
                        issues.append(f"{f}:{i}: {line.strip()}")
        except IOError as e:
            logging.warning(f"Could not read file {f}: {e}")
    if issues:
        add_style_issue("Tabs detected", "\n".join(issues), "Replace all tabs with 4 spaces for consistent indentation")

def check_line_length(sv_files: list[str], max_len: int = 120) -> None:
    """
    Checks for lines exceeding a specified maximum length.

    Args:
        sv_files (list[str]): List of SystemVerilog file paths to check.
        max_len (int): The maximum allowed line length.

    Returns:
        None
    """
    logging.info("Checking line lengths...")
    issues = []
    for f in sv_files:
        try:
            with open(f, 'r', encoding='utf-8', errors='ignore') as file:
                for i, line in enumerate(file, 1):
                    if len(line.rstrip('\n')) > max_len:
                        issues.append(f"{f}:{i}: {line.strip()}")
        except IOError as e:
            logging.warning(f"Could not read file {f}: {e}")
    if issues:
        add_style_issue(f"Lines longer than {max_len} characters", "\n".join(issues), "Break long lines for better readability and code review")

def check_timescale(sv_files: list[str]) -> None:
    """
    Checks for the presence of the `timescale directive.

    Args:
        sv_files (list[str]): List of SystemVerilog file paths to check.

    Returns:
        None
    """
    logging.info("Checking for timescale directive...")
    issues = []
    for f in sv_files:
        try:
            with open(f, 'r', encoding='utf-8', errors='ignore') as file:
                if not any('`timescale' in line for line in file):
                    issues.append(f)
        except IOError as e:
            logging.warning(f"Could not read file {f}: {e}")
    if issues:
        add_critical_issue("Missing timescale directive", "\n".join(issues), "Add `timescale 1ns/1ps as the first line of each file - required for simulation")

def check_default_nettype(sv_files: list[str]) -> None:
    """
    Checks for the presence of the `default_nettype directive.

    Args:
        sv_files (list[str]): List of SystemVerilog file paths to check.

    Returns:
        None
    """
    logging.info("Checking for default_nettype directive...")
    issues = []
    for f in sv_files:
        try:
            with open(f, 'r', encoding='utf-8', errors='ignore') as file:
                if not any('`default_nettype none' in line for line in file):
                    issues.append(f)
        except IOError as e:
            logging.warning(f"Could not read file {f}: {e}")
    if issues:
        add_critical_issue("Missing default_nettype directive", "\n".join(issues), "Add `default_nettype none after timescale - prevents implicit wire declarations")

def check_trailing_whitespace(sv_files: list[str]) -> None:
    """
    Checks for trailing whitespace in SystemVerilog files.

    Args:
        sv_files (list[str]): List of SystemVerilog file paths to check.

    Returns:
        None
    """
    logging.info("Checking for trailing whitespace...")
    issues = []
    for f in sv_files:
        try:
            with open(f, 'r', encoding='utf-8', errors='ignore') as file:
                for i, line in enumerate(file, 1):
                    if line.rstrip() != line.rstrip('\n'):
                        issues.append(f"{f}:{i}: {line.strip()}")
        except IOError as e:
            logging.warning(f"Could not read file {f}: {e}")
    if issues:
        add_style_issue("Trailing whitespace detected", "\n".join(issues), "Remove all trailing spaces and tabs from line endings")

def check_windows_line_endings(sv_files: list[str]) -> None:
    """
    Checks for Windows line endings (CRLF) in SystemVerilog files.

    Args:
        sv_files (list[str]): List of SystemVerilog file paths to check.

    Returns:
        None
    """
    logging.info("Checking for Windows line endings...")
    issues = []
    for f in sv_files:
        try:
            with open(f, 'rb') as file:
                if b'\r\n' in file.read():
                    issues.append(f)
        except IOError as e:
            logging.warning(f"Could not read file {f}: {e}")
    if issues:
        add_style_issue("Windows line endings (CRLF) detected", "\n".join(issues), "Convert CRLF line endings to Unix LF format")

def check_blocking_in_clocked(sv_files: list[str]) -> None:
    """
    Checks for blocking assignments in clocked blocks.

    Args:
        sv_files (list[str]): List of SystemVerilog file paths to check.

    Returns:
        None
    """
    logging.info("Checking for blocking assignments in clocked blocks...")
    issues = []
    clocked_block_re = re.compile(r'always_ff|always\s+@\s*\(\s*posedge')
    blocking_assign_re = re.compile(r'\b[a-zA-Z0-9_]+\s*=(?!=)') # look for = but not ==, <=, >= etc.
    for f in sv_files:
        try:
            with open(f, 'r', encoding='utf-8', errors='ignore') as file:
                in_clocked_block = False
                lines = file.readlines()
                for i, line in enumerate(lines):
                    if 'end' in line:
                        in_clocked_block = False
                    if in_clocked_block and not line.strip().startswith('//') and blocking_assign_re.search(line):
                        issues.append(f"{f}:{i+1}: {line.strip()}")
                    if clocked_block_re.search(line):
                        in_clocked_block = True
        except IOError as e:
            logging.warning(f"Could not read file {f}: {e}")
    if issues:
        add_performance_issue("Blocking assignments in clocked logic", "\n".join(issues), "Use non-blocking assignments (<=) in always_ff blocks to prevent race conditions")

def check_nonblocking_in_comb(sv_files: list[str]) -> None:
    """
    Checks for non-blocking assignments in combinational blocks.

    Args:
        sv_files (list[str]): List of SystemVerilog file paths to check.

    Returns:
        None
    """
    logging.info("Checking for non-blocking assignments in combinational blocks...")
    issues = []
    comb_block_re = re.compile(r'always_comb|always\s+@\s*\(\s*\*')
    nonblocking_assign_re = re.compile(r'<=\s*')
    for f in sv_files:
        try:
            with open(f, 'r', encoding='utf-8', errors='ignore') as file:
                in_comb_block = False
                lines = file.readlines()
                for i, line in enumerate(lines):
                    if 'end' in line:
                        in_comb_block = False
                    if in_comb_block and not line.strip().startswith('//') and nonblocking_assign_re.search(line):
                        issues.append(f"{f}:{i+1}: {line.strip()}")
                    if comb_block_re.search(line):
                        in_comb_block = True
        except IOError as e:
            logging.warning(f"Could not read file {f}: {e}")
    if issues:
        add_performance_issue("Non-blocking assignments in combinational logic", "\n".join(issues), "Use blocking assignments (=) in always_comb blocks for proper simulation behavior")

def check_case_types(sv_files: list[str]) -> None:
    """
    Checks for the use of casez/casex statements.

    Args:
        sv_files (list[str]): List of SystemVerilog file paths to check.

    Returns:
        None
    """
    logging.info("Checking for case statement types...")
    issues = []
    pattern = re.compile(r'\b(casez|casex)\b')
    for f in sv_files:
        try:
            with open(f, 'r', encoding='utf-8', errors='ignore') as file:
                for i, line in enumerate(file, 1):
                    if pattern.search(line) and not line.strip().startswith('//'):
                        issues.append(f"{f}:{i}: {line.strip()}")
        except IOError as e:
            logging.warning(f"Could not read file {f}: {e}")
    if issues:
        add_style_issue("casez/casex statements detected", "\n".join(issues), "Use regular case statements with explicit don't care conditions for better synthesis")

def check_missing_default_in_case(sv_files: list[str]) -> None:
    """
    Checks for case statements that do not have a default clause.

    Args:
        sv_files (list[str]): List of SystemVerilog file paths to check.

    Returns:
        None
    """
    logging.info("Checking for case statements without default...")
    issues = []
    for f in sv_files:
        try:
            with open(f, 'r', encoding='utf-8', errors='ignore') as file:
                content = file.read()
                # A simple regex approach: find 'case' blocks and check for 'default' inside.
                # This is not perfectly robust for nested cases but good for a linter.
                case_blocks = re.findall(r'\bcase\b.*?endcase', content, re.DOTALL)
                case_count = len(re.findall(r'\bcase\b', content))
                default_count = 0
                for block in case_blocks:
                    if 'default' in block:
                        default_count += 1
                if case_count > default_count:
                    issues.append(f"{f} (has {case_count} case statements but only {default_count} default clauses)")
        except IOError as e:
            logging.warning(f"Could not read file {f}: {e}")
    if issues:
        add_best_practice_issue("Missing default cases in case statements", "\n".join(issues), "Add default clause to all case statements to handle unexpected values")

def check_unnamed_generate_blocks(sv_files: list[str]) -> None:
    """
    Checks for unnamed generate blocks (context-aware).

    Args:
        sv_files (list[str]): List of SystemVerilog file paths to check.

    Returns:
        None
    """
    logging.info("Checking for unnamed generate blocks (context-aware)...")
    issues = []
    for f in sv_files:
        try:
            with open(f, 'r', encoding='utf-8', errors='ignore') as file:
                lines = file.readlines()
                in_generate = False
                for i, line in enumerate(lines):
                    # Track generate block entry/exit
                    if re.search(r'\bgenerate\b', line):
                        in_generate = True
                    if re.search(r'\bendgenerate\b', line):
                        in_generate = False
                    if in_generate:
                        # Look for for/if ... begin (no label)
                        m = re.match(r'\s*(for|if)\b.*\bbegin\s*$', line)
                        if m:
                            # Check if 'begin' is followed by ':' and a label on the same line
                            if not re.search(r'begin\s*:\s*\w+', line):
                                issues.append(f"{f}:{i+1}: {line.strip()}")
        except IOError as e:
            logging.warning(f"Could not read file {f}: {e}")
    if issues:
        add_best_practice_issue(
            "Unnamed generate blocks (context-aware)",
            "\n".join(issues),
            "Add labels to all generate blocks (begin : label_name)"
        )

def check_multiple_ports_per_line(sv_files: list[str]) -> None:
    """
    Checks for multiple ports declared on a single line in module headers.

    Args:
        sv_files (list[str]): List of SystemVerilog file paths to check.

    Returns:
        None
    """
    logging.info("Checking for multiple ports per line in module headers...")
    issues = []
    # Regex to match the start of a module header (module ... ()
    module_header_re = re.compile(r'^\s*module\b.*\(')
    # Regex to match the end of a module header ();
    end_header_re = re.compile(r'\)\s*;')
    # Regex to match port declaration keywords
    port_decl_re = re.compile(r'\b(input|output|inout)\b')
    for f in sv_files:
        try:
            with open(f, 'r', encoding='utf-8', errors='ignore') as file:
                lines = file.readlines()
                in_module_header = False
                for i, line in enumerate(lines):
                    # Detect the start of a module header
                    if not in_module_header and module_header_re.search(line):
                        in_module_header = True
                    if in_module_header:
                        # Look for lines with a port declaration and a comma in the port list
                        port_match = port_decl_re.search(line)
                        if port_match:
                            # Remove comments for accurate checking
                            code = line.split('//')[0]
                            # Find the part after the port keyword
                            after_port = code[port_match.end():]
                            # If there's a comma in the port list (not at the end), flag it
                            if ',' in after_port:
                                issues.append(f"{f}:{i+1}: {line.strip()}")
                        # Detect the end of the module header
                        if end_header_re.search(line):
                            in_module_header = False
        except IOError as e:
            logging.warning(f"Could not read file {f}: {e}")
    if issues:
        add_style_issue(
            "Multiple ports per line in module header",
            "\n".join(issues),
            "Declare only one port per line in module headers for readability and maintainability."
        )


def check_single_port_per_line(sv_files: list[str]) -> None:
    """
    Checks that only a single port declaration keyword occurs per line in module headers.

    Args:
        sv_files (list[str]): List of SystemVerilog file paths to check.

    Returns:
        None
    """
    logging.info("Checking for multiple port declarations per line in module headers...")
    issues = []
    # Regex to match the start of a module header
    module_header_re = re.compile(r'^\s*module\b.*\(')
    # Regex to match the end of a module header
    end_header_re = re.compile(r'\)\s*;')
    # Regex to match port declaration keywords
    port_re = re.compile(r'\b(input|output|inout)\b')
    for f in sv_files:
        try:
            with open(f, 'r', encoding='utf-8', errors='ignore') as file:
                lines = file.readlines()
                in_module_header = False
                for i, line in enumerate(lines):
                    # Detect the start of a module header
                    if not in_module_header and module_header_re.search(line):
                        in_module_header = True
                    if in_module_header:
                        # Count how many port keywords are in the line
                        port_matches = list(port_re.finditer(line))
                        if len(port_matches) > 1:
                            issues.append(f"{f}:{i+1}: {line.strip()}")
                        # Detect the end of the module header
                        if end_header_re.search(line):
                            in_module_header = False
        except IOError as e:
            logging.warning(f"Could not read file {f}: {e}")
    if issues:
        add_style_issue(
            "Multiple port declarations per line in module header",
            "\n".join(issues),
            "Declare only one port per line in module headers for readability and maintainability."
        )

def check_unguarded_initial_blocks(filepath: str, lines: list[str]) -> None:
    """
    Detects initial blocks in a SystemVerilog file that are not enclosed within a
    `ifndef SYNTHESIS ... `endif compilation guard.

    Args:
        filepath (str): The path to the SystemVerilog file being checked.
        lines (list[str]): The contents of the file as a list of strings, one per line.

    This function scans through the file line by line, tracking whether the current
    context is inside a synthesis guard. If it encounters an 'initial' block outside
    of such a guard, it records the violation. At the end, if any violations are found,
    it reports them using the add_best_practice_issue() helper function.

    The logic is robust to handle multiple initial blocks and nested or repeated
    synthesis guards within a single file.
    """
    is_in_synth_guard = False
    violations = []
    for idx, line in enumerate(lines, 1):
        # Enter synthesis guard
        if '`ifndef SYNTHESIS' in line:
            is_in_synth_guard = True
        # Exit synthesis guard
        if '`endif' in line and is_in_synth_guard:
            is_in_synth_guard = False
        # Check for unguarded initial block
        if not is_in_synth_guard and re.search(r'\binitial\b', line):
            violations.append(f"{filepath}:{idx}: {line.strip()}")
    if violations:
        add_best_practice_issue(
            "Unguarded initial block(s) detected",
            "\n".join(violations),
            "Wrap all initial blocks in `ifndef SYNTHESIS ... `endif to prevent simulation-only code from being synthesized."
        )

def run_per_file_checks(sv_files: list[str]) -> None:
    """
    Performs per-file checks on each SystemVerilog file.

    Args:
        sv_files (list[str]): List of SystemVerilog file paths to check.

    Returns:
        None
    """
    logging.info("Performing per-file checks...")
    module_re = re.compile(r'^\s*module\b')
    comment_re = re.compile(r'//|/\*')
    non_ansi_re = re.compile(r'^\s*module\s+[a-zA-Z0-9_]+\s*;')
    always_re = re.compile(r'always_(ff|comb)')

    for f in sv_files:
        try:
            with open(f, 'r', encoding='utf-8', errors='ignore') as file:
                lines = file.readlines()
                content = "".join(lines)

                # --- Enhanced Header/Footer Checks ---
                # Header required keys (from IMPLEMENTATION GUIDANCE)
                header_keys = [
                    "// Company:",
                    "// Project Name:",
                    "// File:",
                    "// MODULE_NAME:",
                    "// AUTHOR:",
                    "// VERSION:",
                    "// DATE:",
                    "// DESCRIPTION:",
                    "// PRIMARY_PURPOSE:",
                    "// ROLE_IN_SYSTEM:",
                    "// PROBLEM_SOLVED:",
                    "// MODULE_TYPE:",
                    "// TARGET_TECHNOLOGY_PREF:",
                    "// RELATED_SPECIFICATION:",
                    "// VERIFICATION_STATUS:",
                    "// QUALITY_STATUS:",
                    "`timescale",
                    "`default_nettype none"
                ]
                missing_header_keys = [k for k in header_keys if k not in content]
                if missing_header_keys:
                    add_style_issue(
                        "Missing or incomplete file header",
                        f"{f} (missing: {', '.join(missing_header_keys)})",
                        "Add standard file header with all required fields as per template."
                    )

                # Footer required keys (from IMPLEMENTATION GUIDANCE)
                footer_keys = [
                    "// Dependencies:",
                    "// Instantiated In:",
                    "// Performance:",
                    "// Verification Coverage:",
                    "// Synthesis:",
                    "// Testing:",
                    "// Revision History:",
                    "// Version | Date"
                ]
                missing_footer_keys = [k for k in footer_keys if k not in content]
                if missing_footer_keys:
                    add_style_issue(
                        "Missing or incomplete file footer",
                        f"{f} (missing: {', '.join(missing_footer_keys)})",
                        "Add standard file footer with all required fields as per template."
                    )

                # Check for unbalanced begin/end
                # Only count 'begin' and 'end' as standalone words (not part of 'endmodule', etc.)
                begin_count = len(re.findall(r'\bbegin\b', content))
                end_count = len(re.findall(r'\bend\b', content))
                if begin_count != end_count:
                    add_critical_issue("Unbalanced begin/end blocks", f"{f} (begin: {begin_count}, end: {end_count})", "Fix mismatched begin/end pairs - causes compilation errors")

                # Check for multiple modules
                module_count = len(module_re.findall(content))
                if module_count > 1:
                    add_best_practice_issue("Multiple modules per file", f"{f} ({module_count} modules)", "Split files to contain only one module each for better organization")

                # Check for missing comments
                if not comment_re.search(content):
                    add_best_practice_issue("Files without comments", f, "Add meaningful comments to explain module functionality")

                # Check for non-ANSI module declarations
                if non_ansi_re.search(content):
                    add_best_practice_issue("Non-ANSI module declarations", f, "Convert to ANSI-style port declarations (ports in module header)")

                # Per-line checks
                for i, line in enumerate(lines):
                    # Check for missing comments before always blocks
                    if always_re.search(line):
                        if i > 0 and not comment_re.search(lines[i-1]):
                            add_best_practice_issue("Missing comments before always blocks", f"{f}:{i+1}", "Add descriptive comments before always_ff/always_comb blocks")

                # Check for unguarded initial blocks
                check_unguarded_initial_blocks(f, lines)

        except IOError as e:
            logging.warning(f"Could not read file {f}: {e}")

#===============================================================================
# SECTION 8: FINAL REPORTING AND OUTPUT
#===============================================================================
# Generally no changes needed here unless modifying output format

def autofix_trailing_whitespace_and_line_endings(sv_files: list[str]) -> None:
    """
    Automatically removes trailing whitespace and converts Windows line endings to Unix in-place.

    Args:
        sv_files (list[str]): List of SystemVerilog file paths to fix.

    Returns:
        None
    """
    for f in sv_files:
        try:
            with open(f, 'r', encoding='utf-8', errors='ignore') as file:
                lines = file.readlines()
            # Remove trailing whitespace and convert to Unix line endings
            fixed_lines = [line.rstrip() + '\n' for line in lines]
            with open(f, 'w', encoding='utf-8', newline='\n') as file:
                file.writelines(fixed_lines)
            logging.info(f"Auto-fixed trailing whitespace and line endings in {f}")
        except IOError as e:
            logging.warning(f"Could not auto-fix file {f}: {e}")

def main() -> None:
    """
    Main function to run the linter.

    Returns:
        None
    """
    parser = create_arg_parser()
    args = parser.parse_args()
    
    setup_logging(args.interactive)

    # If no targets and no filelists specified, default to rtl/
    targets = args.targets
    if not targets and not args.filelists:
        targets = ['rtl/']
    # The default=['rtl/'] in argparse handles this, but this is for clarity.
    # If user specifies targets, the default is overridden.
    # If user specifies nothing, the default is used.
    # If user specifies -f but no targets, targets list is empty, so we don't default to rtl/
    if args.filelists and not args.targets:
        targets = []


    logging.info(f"{Colors.BLUE}Running SystemVerilog linter...{Colors.NC}")
    if targets:
        logging.info(f"Targets: {', '.join(targets)}")
    if args.filelists:
        logging.info(f"Filelists: {', '.join(args.filelists)}")
    logging.info(f"Recursive: {args.recursive}")
    logging.info("")

    sv_files = collect_sv_files(targets, args.filelists, args.recursive)

    if not sv_files:
        logging.warning(f"{Colors.YELLOW}No SystemVerilog (.sv) files found in specified targets.{Colors.NC}")
        sys.exit(0)

    # Auto-fix trailing whitespace and line endings if requested
    if getattr(args, 'fix', False):
        logging.info(f"Auto-fixing trailing whitespace and Windows line endings in {len(sv_files)} files...")
        autofix_trailing_whitespace_and_line_endings(sv_files)
        logging.info("Auto-fix complete. Proceeding with lint checks.")

    logging.info(f"Found {len(sv_files)} SystemVerilog files to check:")
    for f in sv_files:
        logging.info(f"  {f}")
    logging.info("")

    # --- Run all checks ---
    check_c_style_braces(sv_files)
    check_tabs(sv_files)
    check_line_length(sv_files)
    check_timescale(sv_files)
    check_default_nettype(sv_files)
    check_trailing_whitespace(sv_files)
    check_windows_line_endings(sv_files)
    check_blocking_in_clocked(sv_files)
    check_nonblocking_in_comb(sv_files)
    check_case_types(sv_files)
    check_missing_default_in_case(sv_files)
    run_per_file_checks(sv_files) # This combines multiple per-file checks
    check_unnamed_generate_blocks(sv_files) # Context-aware unnamed generate block check
    check_multiple_ports_per_line(sv_files) # Multiple ports per line in module header
    check_single_port_per_line(sv_files) # Single port per line in module header

    # --- Final Summary ---
    logging.info("")
    if fail:
        logging.error(f"{Colors.RED}ERROR: SystemVerilog linting issues detected in files.{Colors.NC}")
        logging.error(f"{Colors.YELLOW}Total issue categories found: {total_issues}{Colors.NC}")
        logging.info("")
        llm_prompt = generate_llm_prompt(sv_files)
        # The LLM prompt is the primary output of the script, so it's printed to stdout
        # instead of being logged, allowing for redirection.
        # Also write the LLM prompt to a dedicated output file for user/automation.
        with open('lint_sv_blocks.out', 'w', encoding='utf-8') as out_f:
            out_f.write(llm_prompt)
        print(llm_prompt)
        sys.exit(1)
    else:
        logging.info(f"{Colors.GREEN}✓ SystemVerilog block style and lint checks passed.{Colors.NC}")
        logging.info("All files conform to coding standards.")
        sys.exit(0)

if __name__ == "__main__":
    main()
