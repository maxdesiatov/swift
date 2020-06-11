/// other ==> main | yet-another
/// other ==> main +==> yet-another

// RUN: %empty-directory(%t)
// RUN: cp -r %S/Inputs/chained-after-fine/* %t
// RUN: touch -t 201401240005 %t/*.swift

// Generate the build record...
// RUN: cd %t && %swiftc_driver -c -driver-use-frontend-path "%{python};%S/Inputs/update-dependencies.py;%swift-dependency-tool" -output-file-map %t/output.json -incremental -driver-always-rebuild-dependents -enable-direct-intramodule-dependencies ./main.swift ./other.swift ./yet-another.swift -module-name main -j1 -v

// ...then reset the .swiftdeps files.
// RUN: cp -r %S/Inputs/chained-after-fine/*.swiftdeps %t
// RUN: cd %t && %swiftc_driver -c -driver-use-frontend-path "%{python};%S/Inputs/update-dependencies.py;%swift-dependency-tool" -output-file-map %t/output.json -incremental -driver-always-rebuild-dependents -enable-direct-intramodule-dependencies ./main.swift ./other.swift ./yet-another.swift -module-name main -j1 -v 2>&1 | %FileCheck -check-prefix=CHECK-FIRST %s

// CHECK-FIRST-NOT: warning
// CHECK-FIRST-NOT: Handled

// RUN: touch -t 201401240006 %t/other.swift
// RUN: cd %t && %swiftc_driver -c -driver-use-frontend-path "%{python};%S/Inputs/update-dependencies.py;%swift-dependency-tool" -output-file-map %t/output.json -incremental -driver-always-rebuild-dependents -enable-direct-intramodule-dependencies ./yet-another.swift ./main.swift ./other.swift -module-name main -j1 -v 2>&1 | %FileCheck -check-prefix=CHECK-THIRD %s

// CHECK-THIRD: Handled main.swift
// CHECK-THIRD: Handled other.swift
// CHECK-THIRD: Handled yet-another.swift
