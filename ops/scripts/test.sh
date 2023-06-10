# peltak:
#   root_cli: true
#   about: Run tests
#   options:
#     - name: ['-k', '--kind']
#       about: |
#         What kind of tests should be ran (all/unit/e2e/doctest). If not given,
#         then alltests will run.
#       type: str
#       default: all
#     - name: ['-no-sugar']
#       about: Disable pytest-sugar. Might be useful for CI runs.
#       is_flag: true
#     - name: ['--cov-xml']
#       about: Generate junit XML coverage report. Useful for 3rd party integrations.
#       is_flag: true
#     - name: ['--cov']
#       about: |
#         What type of coverage should we define. Allowed values are:
#         all/core/scripts/extra. Defaults to 'all'.
#       type: str
#       default: all
#   use:
#     - cprint
#     - header



{% set cov_html_path = conf.build_dir  + '/coverage' %}

{% if opts.kind in ('all', 'doctest') %}
  {{ "Running doctests" | header }}
  PYTHONPATH=src pytest \
    --doctest-modules \
    --doctest-report ndiff \
    {{ ctx.verbose | count_flag('v') }} \
    {{ '-p no:sugar' if opts.no_sugar else '' }} \
    src/{{ pkg_name }}

  # We do not fail if there are not doctests (would prevent running tests below).
  if [ $# -ne 0 ] && [ $# -ne 5 ]; then
    exit 127
  fi
{% endif %}

set -e

{% if opts.kind != 'doctest' %}
  {{ "Running tests" | header }}
  pytest \
    --cov=src/{{ pkg_name }} \
    --cov-report=term:skip-covered \
    --cov-report=html:{{ cov_html_path }} \
    {{ '--cov-report=xml' if opts.cov_xml else '' }} \
    {{ ctx.verbose | count_flag('v') }} \
    {{ '-p no:sugar' if opts.no_sugar else '' }} \
    tests
{% endif %}


{% if opts.kind != 'doctest' %}
  {% set cov_path = proj_path(cov_html_path, 'index.html') %}
  {{ '\n<32>HTML report: <34>file://{}' | cprint(cov_path) }}
{% endif %}

