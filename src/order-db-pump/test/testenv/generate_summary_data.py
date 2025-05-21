import os

os.system("python app_coverage.py")
os.system("python total_coverage.py")

with open(os.path.join("reports", "app_coverage.txt"), "r") as app_coverage_file:
    app_coverage = app_coverage_file.read()

with open(os.path.join("reports", "total_coverage.txt"), "r") as total_coverage_file:
    total_coverage = total_coverage_file.read()

coverage_report = u"""<section name="Code Coverage">"""
coverage_report += u"""<field name="App Coverage" value="{}%"></field>""".format(app_coverage)
coverage_report += u"""<field name="Total Coverage" value="{}%"></field>""".format(total_coverage)
coverage_report += u"""</section>"""

coverage_section_path = os.path.join(u"reports", u"coverage_section.xml")
with open(coverage_section_path, u"wb") as summary_file:
    summary_file.write(coverage_report.encode(u"utf-8"))
