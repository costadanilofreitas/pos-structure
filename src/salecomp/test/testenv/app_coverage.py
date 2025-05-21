import os
import coverage

cov = coverage.Coverage(config_file=".coveragerc")
cov.start()

import run_all_unit_tests_no_exit
run_all_unit_tests_no_exit.main()

cov.stop()
cov.save()

app_coverage = cov.report()
cov.xml_report(outfile=os.path.join("reports", "coverage.xml"))

reports_path = os.path.abspath("reports")
if not os.path.exists(reports_path):
    os.makedirs(reports_path)
with open(os.path.join(reports_path, "app_coverage.txt"), "wb") as file:
    file.write("{:.2f}".format(app_coverage).encode("utf-8"))
