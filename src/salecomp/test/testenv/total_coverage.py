import os
import coverage

cov = coverage.Coverage(config_file=".totalcoveragerc")
cov.start()

import run_all_unit_tests_no_exit
run_all_unit_tests_no_exit.main()

cov.stop()
cov.save()

cov.html_report(directory="htmlcov")
total_coverage = cov.report()

reports_path = os.path.abspath("reports")
if not os.path.exists(reports_path):
    os.makedirs(reports_path)
with open(os.path.join(reports_path, "total_coverage.txt"), "wb") as file:
    file.write("{:.2f}".format(total_coverage).encode("utf-8"))
