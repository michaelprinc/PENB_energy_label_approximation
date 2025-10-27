poml<spec agent="github-copilot" version="1.0">

<pre_flight>
  <gather>
    <item>Goal and constraints (perf, security, deadlines)</item>
    <item>Repo structure and entry points</item>
    <item>Existing reusable code (prefer extend over rewrite)</item>
    <item>Default language: python (.py) unless specified</item>
  </gather>
</pre_flight>

<task>
  <phase name="plan">
    <step>Produce a 3–5 step checklist WITH acceptance criteria.</step>
    <step>Audit repo for reuse opportunities and dependencies.</step>
    <step>Identify risks and required confirmations.</step>
  </phase>

  <phase name="execute">
    <step>Mark checklist progress: [ ] → [x].</step>
    <step>Write/modify code in project files (not chat).</step>
    <step>Show minimal git diff preview before commit.</step>
    <step>Commit atomic changes with clear messages.</step>
  </phase>

  <phase name="verify">
    <step>Run tests, lint, type checks, and build if relevant.</step>
    <step>Report results succinctly.</step>
    <step>Declare DONE or provide next TODO step.</step>
  </phase>
</task>

<completion_criteria>
  <rule>MVP first, iterate after feedback.</rule>
  <rule>All tests/checks pass and diff reviewed.</rule>
  <rule>Code stored in .py files by default.</rule>
  <rule>Acceptance criteria met.</rule>
</completion_criteria>

<guardrails>
  <security>
    <rule>Never commit secrets/tokens.</rule>
    <rule>Ensure .gitignore covers credentials and artifacts.</rule>
    <rule>Use environment variables or secret stores.</rule>
  </security>
  <quality>
    <rule>Add/extend tests alongside code changes.</rule>
    <rule>Run lint and type checks; fix blockers.</rule>
    <rule>Pin dependency versions (lockfiles or exact pins).</rule>
  </quality>
  <risk_management>
    <rule>No new dependencies without permission.</rule>
    <rule>Confirm destructive ops (rm, force-push, schema changes).</rule>
    <rule>Provide explicit rollback steps for risky changes.</rule>
  </risk_management>
</guardrails>

<terminal_protocol>
  <proposal>
    <action></action>         <!-- exact command -->
    <purpose></purpose>       <!-- why this is needed -->
    <risk>low|medium|high</risk>
    <undo></undo>             <!-- rollback command/steps -->
  </proposal>
  <execution>
    <rule>Await CONFIRM for any destructive action.</rule>
    <rule>Log outcomes and update checklist state.</rule>
  </execution>
</terminal_protocol>

<complexity>
  <definition>
    <rule>Touches ≥2 modules/services OR introduces a new service/DB/SDK.</rule>
    <rule>Includes migrations, infra changes, or other destructive ops.</rule>
    <rule>Requirements are ambiguous or require external coordination.</rule>
    <rule>Estimated effort &gt; 60 minutes OR &gt; 50 LOC changed across files.</rule>
  </definition>
  <is_complex>TRUE if any rule matches; otherwise FALSE.</is_complex>
  <report required_when="TRUE" name_format="reports/{YYYYMMDD-HHmmss}_{report_name}.md" timezone="local">
    <must_include>
      <item>Goal, scope, constraints, assumptions.</item>
      <item>Architecture/flow (ASCII diagram acceptable).</item>
      <item>Plan checklist with owners and timestamps.</item>
      <item>Risk analysis, confirmation points, rollback steps.</item>
      <item>Links to diffs, tests, artifacts, and follow-ups.</item>
    </must_include>
  </report>
</complexity>

<response_templates>
  <simple_task>
    PLAN:
    - [ ] Define acceptance criteria (MVP first)
    - [ ] Check reusable code and deps
    - [ ] Implement in .py file
    - [ ] Add/extend tests
    - [ ] Run lint/type/tests

    FILES: <path>:<summary_of_changes>
    DIFF: <minimal_preview>
    CHECK: <test_lint_build_results>
    STATUS: DONE | TODO: <next_step>
  </simple_task>

  <error_handling>
    ATTEMPT: <what_was_tried>
    ERROR: <short_summary>
    CAUSE: <likely_reason>
    FIX: <one_or_two_options>
    REQUEST: CONFIRM option or provide more context
  </error_handling>
</response_templates>

<optimization_rules>
  <rule>Prefer the smallest viable change that meets DoD.</rule>
  <rule>Compose over inherit; prefer pure functions over stateful.</rule>
  <rule>Ask at most one clarification; otherwise present two concrete paths.</rule>
  <rule>Stop after two failed attempts and request direction.</rule>
</optimization_rules>

<allowed_commands>
  <safe>mv, cp, mkdir, touch, git add, git commit</safe>
  <confirm_required>rm, git reset --hard, force-push, db migrations</confirm_required>
  <package_managers>npm, pip, poetry (with pinned versions)</package_managers>
</allowed_commands>

</spec>