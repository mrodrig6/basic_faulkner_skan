# SciPy comparison

`test_dense_output_matches_scipy` compares the compiled dense-output integrator against SciPy RK45 on the same initial-value problem. This isolates integration and interpolation from the shooting method.

```python
import numpy as np
from scipy.integrate import solve_ivp
from falkner_skan._kernels import integrate

n, shear, eta_max = 0.05, 0.42, 8.0
eta = np.linspace(0.0, eta_max, 401)
y = np.empty((eta.size, 3))
integrate(n, shear, eta_max, 1e-10, 1e-12, eta, y)
reference = solve_ivp(
    lambda _, f: [f[1], f[2], n * (f[1] ** 2 - 1) - 0.5 * (n + 1) * f[0] * f[2]],
    (0.0, eta_max), (0.0, 0.0, shear),
    method="RK45", rtol=1e-10, atol=1e-12, t_eval=eta,
)
assert reference.success
error = np.max(np.abs(reference.y.T - y))
assert error < 1e-9
print(f"maximum absolute difference: {error:.2e}")
```

```text
maximum absolute difference: 4.44e-15
```

The acceptance criterion is an absolute difference below `1e-9`, approximately nine decimal places in these dimensionless values. The final digits can vary by dependency version and platform. This does not test the SciPy DOP853 fallback’s shooting loop; see [backends](../method/backends.md).
