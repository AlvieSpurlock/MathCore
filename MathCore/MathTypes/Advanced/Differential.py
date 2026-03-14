import math  # sqrt, pi, cos, sin, acos, atan2

# Curves are passed as callables:  curve(t) -> [x, y, z]
# Surfaces are passed as callables: surface(u, v) -> [x, y, z]
# Differential forms use callable coefficient functions f(x, y, z) -> float.
# All numerical derivatives use central differences for O(h²) accuracy.
# Matrices are lists of lists (row-major); vectors are plain lists.

# ============================================================
# INTERNAL HELPERS  (prefixed _ — not part of public API)
# ============================================================

_H  = 1e-5   # Step size for first/second derivatives
_H3 = 5e-4   # Larger step for third derivative (reduces cancellation error)

def _d1(f, t, h=_H):
    """First derivative of a scalar or vector-valued function (central difference)."""
    fp = f(t + h); fm = f(t - h)
    if isinstance(fp, (list, tuple)):
        return [(fp[i] - fm[i]) / (2.0 * h) for i in range(len(fp))]
    return (fp - fm) / (2.0 * h)

def _d2(f, t, h=_H):
    """Second derivative: (f(t+h) - 2f(t) + f(t-h)) / h²."""
    fp = f(t + h); fc = f(t); fm = f(t - h)
    if isinstance(fp, (list, tuple)):
        return [(fp[i] - 2.0*fc[i] + fm[i]) / (h*h) for i in range(len(fp))]
    return (fp - 2.0*fc + fm) / (h*h)

def _d3(f, t, h=_H3):
    """Third derivative: (f(t+2h) - 2f(t+h) + 2f(t-h) - f(t-2h)) / (2h³)."""
    f2p = f(t + 2.0*h); f1p = f(t + h)
    f1m = f(t - h);     f2m = f(t - 2.0*h)
    denom = 2.0 * h**3
    if isinstance(f2p, (list, tuple)):
        return [(f2p[i] - 2.0*f1p[i] + 2.0*f1m[i] - f2m[i]) / denom
                for i in range(len(f2p))]
    return (f2p - 2.0*f1p + 2.0*f1m - f2m) / denom

def _norm(v):    return math.sqrt(sum(x*x for x in v))
def _normalize(v):
    m = _norm(v)
    return [x/m for x in v] if m > 1e-14 else [0.0]*len(v)
def _dot(a,b):   return sum(a[i]*b[i] for i in range(len(a)))
def _cross(a,b): return [a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0]]
def _add(a,b):   return [a[i]+b[i] for i in range(len(a))]
def _sub(a,b):   return [a[i]-b[i] for i in range(len(a))]
def _scale(c,v): return [c*x for x in v]

def _pu(S,u,v,h=_H):
    return [(S(u+h,v)[i]-S(u-h,v)[i])/(2.0*h) for i in range(3)]
def _pv(S,u,v,h=_H):
    return [(S(u,v+h)[i]-S(u,v-h)[i])/(2.0*h) for i in range(3)]
def _puu(S,u,v,h=_H):
    sp=S(u+h,v); sc=S(u,v); sm=S(u-h,v)
    return [(sp[i]-2.0*sc[i]+sm[i])/(h*h) for i in range(3)]
def _pvv(S,u,v,h=_H):
    sp=S(u,v+h); sc=S(u,v); sm=S(u,v-h)
    return [(sp[i]-2.0*sc[i]+sm[i])/(h*h) for i in range(3)]
def _puv(S,u,v,h=_H):
    pp=S(u+h,v+h); pm=S(u+h,v-h); mp=S(u-h,v+h); mm=S(u-h,v-h)
    return [(pp[i]-pm[i]-mp[i]+mm[i])/(4.0*h*h) for i in range(3)]

# ============================================================
# CURVES IN ℝ³
# ============================================================

# Formula: γ'(t) — velocity vector of a parametric curve at parameter t
# Returns [dx/dt, dy/dt, dz/dt] via central difference
def CurveTangentVector(curve, t, h=_H):
    return _d1(curve, t, h)                                    # Central difference → γ'(t)

# Formula: ‖γ'(t)‖ — speed (magnitude of velocity) at parameter t
def CurveSpeed(curve, t, h=_H):
    return _norm(CurveTangentVector(curve, t, h))               # ‖γ'(t)‖ → speed

# Formula: T(t) = γ'(t) / ‖γ'(t)‖ — unit tangent vector
def UnitTangent(curve, t, h=_H):
    return _normalize(CurveTangentVector(curve, t, h))          # Normalise velocity → T(t)

# Formula: γ''(t) — acceleration vector at parameter t
def CurveAcceleration(curve, t, h=_H):
    return _d2(curve, t, h)                                     # Second derivative → γ''(t)

# Formula: κ(t) = ‖γ'(t) × γ''(t)‖ / ‖γ'(t)‖³
# Returns the curvature — how sharply the curve bends; zero for straight lines
def Curvature(curve, t, h=_H):
    v   = CurveTangentVector(curve, t, h)
    a   = CurveAcceleration(curve, t, h)
    spd = _norm(v)
    if spd < 1e-14:
        return 0.0
    return _norm(_cross(v, a)) / spd**3                        # Complete κ = ‖v×a‖ / ‖v‖³

# Formula: ρ(t) = 1 / κ(t) — radius of curvature
def RadiusOfCurvature(curve, t, h=_H):
    k = Curvature(curve, t, h)
    return 1.0/k if k > 1e-14 else float('inf')                # ρ = 1/κ

# Formula: τ(t) = (γ' × γ'') · γ''' / ‖γ' × γ''‖²
# Returns the torsion — how much the curve twists out of its osculating plane
def Torsion(curve, t, h=_H):
    v     = CurveTangentVector(curve, t, h)
    a     = CurveAcceleration(curve, t, h)
    j     = _d3(curve, t)                                      # γ'''(t) via correct 5-point formula
    vxa   = _cross(v, a)
    denom = _norm(vxa)**2
    if denom < 1e-14:
        return 0.0                                              # Planar curve → zero torsion
    return _dot(vxa, j) / denom                                # Complete τ = (v×a)·j / ‖v×a‖²

# Formula: L = ∫ₐᵇ ‖γ'(t)‖ dt — arc length via composite Simpson's rule
def ArcLength(curve, a, b, n=1000):
    if n % 2: n += 1
    h = (b-a)/n
    s = CurveSpeed(curve, a) + CurveSpeed(curve, b)
    for i in range(1, n):
        s += (4 if i%2 else 2) * CurveSpeed(curve, a+i*h)
    return s*h/3.0                                             # Complete Simpson arc length

# Returns (t_vals, s_vals) lookup tables for arc-length reparametrization
def ArcLengthTable(curve, a, b, n=500):
    h = (b-a)/n
    s_vals = [0.0]
    for i in range(1, n+1):
        t0=a+(i-1)*h; t1=a+i*h; tm=(t0+t1)/2.0
        s_vals.append(s_vals[-1] + (CurveSpeed(curve,t0)+4.0*CurveSpeed(curve,tm)+CurveSpeed(curve,t1))*h/6.0)
    return [a+i*h for i in range(n+1)], s_vals                # (t_vals, s_vals)

# ============================================================
# FRENET-SERRET FRAME
# ============================================================

# Formula: T = γ'/‖γ'‖,  N = T'/‖T'‖,  B = T × N
# Returns (T, N, B) — the orthonormal Frenet-Serret frame at parameter t
def FrenetSerretFrame(curve, t, h=_H):
    T  = UnitTangent(curve, t, h)
    dT = _d1(lambda s: UnitTangent(curve, s, h), t, h)         # Rate of change of unit tangent
    N  = _normalize(dT)                                        # Principal normal
    B  = _cross(T, N)                                          # Binormal B = T × N
    return T, N, B                                             # Complete Frenet-Serret triad (T, N, B)

# Returns (κ, τ) — curvature and torsion confirming the Frenet-Serret equations
def FrenetSerretCurvatureTorsion(curve, t, h=_H):
    return Curvature(curve, t, h), Torsion(curve, t, h)

# Formula: osculating plane normal = B; plane passes through γ(t)
def OsculatingPlane(curve, t, h=_H):
    T, N, B = FrenetSerretFrame(curve, t, h)
    return B, curve(t)                                         # (normal, base point)

# Formula: osculating circle — center = γ(t) + ρN, radius = 1/κ
def OsculatingCircle(curve, t, h=_H):
    _, N, _ = FrenetSerretFrame(curve, t, h)
    kappa   = Curvature(curve, t, h)
    if kappa < 1e-14:
        return None, float('inf')
    rho = 1.0/kappa
    return _add(curve(t), _scale(rho, N)), rho                 # (center, radius)

# Formula: ∫κ ds and ∫τ ds over [a,b] — total curvature and total torsion
def TotalCurvatureAndTorsion(curve, a, b, n=500):
    h = (b-a)/n; tk = tt = 0.0
    for i in range(n):
        ti  = a+(i+0.5)*h; sp = CurveSpeed(curve, ti)
        tk += Curvature(curve, ti)*sp*h
        tt += Torsion(curve, ti)*sp*h
    return tk, tt                                              # (∫κ ds, ∫τ ds)

# ============================================================
# PARAMETRIC SURFACES
# ============================================================

# Formula: rᵤ = ∂r/∂u, rᵥ = ∂r/∂v — tangent vectors spanning the tangent plane
def SurfaceTangentVectors(surface, u, v, h=_H):
    return _pu(surface,u,v,h), _pv(surface,u,v,h)              # (r_u, r_v)

# Formula: N = rᵤ × rᵥ — surface normal (unnormalised; ‖N‖ = area element)
def SurfaceNormal(surface, u, v, h=_H):
    ru,rv = SurfaceTangentVectors(surface,u,v,h)
    return _cross(ru, rv)                                      # N = rᵤ × rᵥ

# Formula: n̂ = N / ‖N‖ — unit normal
def UnitNormal(surface, u, v, h=_H):
    return _normalize(SurfaceNormal(surface,u,v,h))

# Formula: dA = ‖rᵤ × rᵥ‖ du dv — area element magnitude
def AreaElement(surface, u, v, h=_H):
    return _norm(SurfaceNormal(surface,u,v,h))

# Formula: ∫∫ ‖rᵤ × rᵥ‖ du dv — surface area via midpoint rule on n×n grid
def SurfaceArea(surface, u0, u1, v0, v1, n=50):
    du=(u1-u0)/n; dv=(v1-v0)/n; total=0.0
    for i in range(n):
        for j in range(n):
            total += AreaElement(surface, u0+(i+0.5)*du, v0+(j+0.5)*dv)*du*dv
    return total

# ============================================================
# FIRST FUNDAMENTAL FORM
# ============================================================

# Formula: E = rᵤ·rᵤ, F = rᵤ·rᵥ, G = rᵥ·rᵥ
# I = E du² + 2F du dv + G dv² — measures lengths and angles intrinsically
def FirstFundamentalForm(surface, u, v, h=_H):
    ru,rv = SurfaceTangentVectors(surface,u,v,h)
    return _dot(ru,ru), _dot(ru,rv), _dot(rv,rv)               # (E, F, G)

# Returns the 2×2 metric tensor [[E,F],[F,G]]
def MetricTensor(surface, u, v, h=_H):
    E,F,G = FirstFundamentalForm(surface,u,v,h)
    return [[E,F],[F,G]]

# Formula: ds² = E du² + 2F du dv + G dv² — squared arc-length in direction (du,dv)
def ArcLengthElement(surface, u, v, du, dv, h=_H):
    E,F,G = FirstFundamentalForm(surface,u,v,h)
    return E*du*du + 2.0*F*du*dv + G*dv*dv

# Formula: θ = arccos(F / √(EG)) — angle between coordinate curves at (u,v)
def AngleBetweenCoordinateCurves(surface, u, v, h=_H):
    E,F,G = FirstFundamentalForm(surface,u,v,h)
    d = math.sqrt(E*G)
    if d < 1e-14: return 0.0
    return math.degrees(math.acos(max(-1.0, min(1.0, F/d))))   # Complete θ = arccos(F/√EG)

# Formula: √(EG − F²) — area-scaling factor (square root of metric determinant)
def MetricDeterminant(surface, u, v, h=_H):
    E,F,G = FirstFundamentalForm(surface,u,v,h)
    return math.sqrt(max(0.0, E*G - F*F))

# ============================================================
# SECOND FUNDAMENTAL FORM
# ============================================================

# Formula: L = rᵤᵤ·n̂,  M = rᵤᵥ·n̂,  N = rᵥᵥ·n̂
# II = L du² + 2M du dv + N dv² — encodes extrinsic curvature
def SecondFundamentalForm(surface, u, v, h=_H):
    n_hat = UnitNormal(surface,u,v,h)
    L = _dot(_puu(surface,u,v,h), n_hat)
    M = _dot(_puv(surface,u,v,h), n_hat)
    N = _dot(_pvv(surface,u,v,h), n_hat)
    return L, M, N                                             # Complete (L, M, N)

# Formula: κₙ = II / I = (L du² + 2M du dv + N dv²) / (E du² + 2F du dv + G dv²)
def NormalCurvature(surface, u, v, du, dv, h=_H):
    L,M,N = SecondFundamentalForm(surface,u,v,h)
    num   = L*du*du + 2.0*M*du*dv + N*dv*dv
    den   = ArcLengthElement(surface,u,v,du,dv,h)
    return num/den if abs(den) > 1e-14 else 0.0                # Complete κₙ = II/I

# ============================================================
# SURFACE CURVATURE
# ============================================================

# Formula: shape operator S = I⁻¹ · II — 2×2 Weingarten map (eigenvalues = principal curvatures)
def ShapeOperator(surface, u, v, h=_H):
    E,F,G = FirstFundamentalForm(surface,u,v,h)
    L,M,N = SecondFundamentalForm(surface,u,v,h)
    det_I = E*G - F*F
    if abs(det_I) < 1e-14: return [[0.0,0.0],[0.0,0.0]]
    return [[(G*L-F*M)/det_I, (G*M-F*N)/det_I],
            [(E*M-F*L)/det_I, (E*N-F*M)/det_I]]               # Complete shape operator

# Formula: K = (LN − M²) / (EG − F²) — Gaussian curvature (Theorema Egregium)
# K > 0 elliptic, K < 0 hyperbolic, K = 0 parabolic/flat
def GaussianCurvature(surface, u, v, h=_H):
    E,F,G = FirstFundamentalForm(surface,u,v,h)
    L,M,N = SecondFundamentalForm(surface,u,v,h)
    det_I = E*G - F*F
    return (L*N - M*M)/det_I if abs(det_I) > 1e-14 else 0.0   # Complete K

# Formula: H = (EN − 2FM + GL) / (2(EG − F²)) — mean curvature
# H = 0 for minimal surfaces; |H| = 1/r for a sphere of radius r
def MeanCurvature(surface, u, v, h=_H):
    E,F,G = FirstFundamentalForm(surface,u,v,h)
    L,M,N = SecondFundamentalForm(surface,u,v,h)
    det_I = E*G - F*F
    return (E*N - 2.0*F*M + G*L)/(2.0*det_I) if abs(det_I) > 1e-14 else 0.0

# Formula: κ₁ = H + √(H²−K), κ₂ = H − √(H²−K) — principal curvatures
# Returns (kappa1, kappa2) with kappa1 ≥ kappa2
def PrincipalCurvatures(surface, u, v, h=_H):
    K=GaussianCurvature(surface,u,v,h); H=MeanCurvature(surface,u,v,h)
    sq = math.sqrt(max(0.0, H*H - K))
    return H+sq, H-sq                                         # κ₁ ≥ κ₂

# Returns 'elliptic', 'hyperbolic', 'parabolic', or 'flat' at the surface point
def ClassifySurfacePoint(surface, u, v, h=_H, tol=1e-6):
    K=GaussianCurvature(surface,u,v,h); H=MeanCurvature(surface,u,v,h)
    if   K >  tol: return 'elliptic'
    elif K < -tol: return 'hyperbolic'
    elif abs(H) > tol: return 'parabolic'
    else: return 'flat (planar)'

# Formula: ∫∫ K dA — total Gaussian curvature over parameter rectangle [u0,u1]×[v0,v1]
def TotalGaussianCurvature(surface, u0, u1, v0, v1, n=40):
    du=(u1-u0)/n; dv=(v1-v0)/n; total=0.0
    for i in range(n):
        for j in range(n):
            u=u0+(i+0.5)*du; v=v0+(j+0.5)*dv
            total += GaussianCurvature(surface,u,v)*MetricDeterminant(surface,u,v)*du*dv
    return total                                               # Complete ∫∫ K dA

# ============================================================
# CHRISTOFFEL SYMBOLS
# ============================================================

# Formula: Γᵏᵢⱼ = ½ gᵏˡ (∂ⱼgᵢˡ + ∂ᵢgⱼˡ − ∂ˡgᵢⱼ) — Christoffel symbols of the second kind
# Indices: 0 ↔ u, 1 ↔ v. Returns Γ[k][i][j] — a 2×2×2 array at (u,v)
def ChristoffelSymbols(surface, u, v, h=_H):
    def g_at(uu,vv):
        E,F,G=FirstFundamentalForm(surface,uu,vv,h); return [[E,F],[F,G]]
    g0=g_at(u,v); gup=g_at(u+h,v); gum=g_at(u-h,v); gvp=g_at(u,v+h); gvm=g_at(u,v-h)
    dg = [
        [[(gup[i][j]-gum[i][j])/(2.0*h) for j in range(2)] for i in range(2)],
        [[(gvp[i][j]-gvm[i][j])/(2.0*h) for j in range(2)] for i in range(2)],
    ]
    E0,F0,G0=g0[0][0],g0[0][1],g0[1][1]; det=E0*G0-F0*F0
    if abs(det)<1e-14: return [[[0.0]*2 for _ in range(2)] for _ in range(2)]
    gi=[[G0/det,-F0/det],[-F0/det,E0/det]]
    G3=[[[0.0]*2 for _ in range(2)] for _ in range(2)]
    for k in range(2):
        for i in range(2):
            for j in range(2):
                G3[k][i][j]=0.5*sum(gi[k][l]*(dg[j][i][l]+dg[i][j][l]-dg[l][i][j])
                                    for l in range(2))        # Complete Γᵏᵢⱼ
    return G3

# Formula: (DV/dt)ᵏ = (dV/dt)ᵏ + Γᵏᵢⱼ σ'ⁱ Vʲ — covariant derivative of V along a curve
def CovariantDerivative(surface, u, v, V, sigma_prime, dV_dt, h=_H):
    G3=ChristoffelSymbols(surface,u,v,h); result=list(dV_dt)
    for k in range(2):
        for i in range(2):
            for j in range(2):
                result[k] += G3[k][i][j]*sigma_prime[i]*V[j]
    return result                                              # Complete covariant derivative

# Formula: DV/dt = 0 iff V is parallel-transported along the curve
def IsParallelTransport(surface, u, v, V, sigma_prime, dV_dt, tol=1e-4, h=_H):
    DV=CovariantDerivative(surface,u,v,V,sigma_prime,dV_dt,h)
    return all(abs(DV[k])<tol for k in range(2))

# ============================================================
# GEODESICS
# ============================================================

# Formula: geodesic equation  ü^k + Γᵏᵢⱼ u̇ⁱ u̇ʲ = 0
# Integrates using 4th-order Runge-Kutta; returns list of (u,v) parameter pairs
def GeodesicPath(surface, u0, v0, du0, dv0, s_max=2.0, n=400):
    dt=s_max/n; state=[float(u0),float(v0),float(du0),float(dv0)]; path=[(state[0],state[1])]
    def drv(s):
        u,v,du,dv=s; G3=ChristoffelSymbols(surface,u,v)
        ddu=-(G3[0][0][0]*du*du+2.0*G3[0][0][1]*du*dv+G3[0][1][1]*dv*dv)
        ddv=-(G3[1][0][0]*du*du+2.0*G3[1][0][1]*du*dv+G3[1][1][1]*dv*dv)
        return [du,dv,ddu,ddv]
    for _ in range(n):
        k1=drv(state); k2=drv([state[i]+0.5*dt*k1[i] for i in range(4)])
        k3=drv([state[i]+0.5*dt*k2[i] for i in range(4)])
        k4=drv([state[i]+dt*k3[i] for i in range(4)])
        state=[state[i]+dt*(k1[i]+2.0*k2[i]+2.0*k3[i]+k4[i])/6.0 for i in range(4)]
        path.append((state[0],state[1]))
    return path                                                # Complete geodesic (u,v) path

# Returns the total metric arc length of a geodesic path list [(u,v),...]
def GeodesicLength(surface, path):
    total=0.0
    for i in range(1, len(path)):
        u0,v0=path[i-1]; u1,v1=path[i]; um,vm=(u0+u1)/2.0,(v0+v1)/2.0
        E,F,G=FirstFundamentalForm(surface,um,vm); du,dv=u1-u0,v1-v0
        total+=math.sqrt(max(0.0,E*du*du+2.0*F*du*dv+G*dv*dv))
    return total

# Returns True if σ(t) satisfies the geodesic equations at t (within tolerance)
def IsGeodesic(surface, sigma, t, tol=1e-3, h=_H):
    du =_d1(lambda s:sigma(s)[0],t,h); dv =_d1(lambda s:sigma(s)[1],t,h)
    ddu=_d2(lambda s:sigma(s)[0],t,h); ddv=_d2(lambda s:sigma(s)[1],t,h)
    u,v=sigma(t); G3=ChristoffelSymbols(surface,u,v,h)
    eu=ddu+G3[0][0][0]*du*du+2.0*G3[0][0][1]*du*dv+G3[0][1][1]*dv*dv
    ev=ddv+G3[1][0][0]*du*du+2.0*G3[1][0][1]*du*dv+G3[1][1][1]*dv*dv
    return abs(eu)<tol and abs(ev)<tol

# ============================================================
# DIFFERENTIAL FORMS
# ============================================================

# Formula: df = (∂f/∂x)dx + (∂f/∂y)dy + (∂f/∂z)dz — exterior derivative of 0-form f
# Returns 1-form coefficients [∂f/∂x, ∂f/∂y, ∂f/∂z] at (x,y,z)
def ExteriorDerivative0Form(f, x, y, z, h=_H):
    return [(f(x+h,y,z)-f(x-h,y,z))/(2.0*h),
            (f(x,y+h,z)-f(x,y-h,z))/(2.0*h),
            (f(x,y,z+h)-f(x,y,z-h))/(2.0*h)]                 # Complete gradient 1-form

# Formula: dω for ω = P dx + Q dy + R dz
# dω = (∂R/∂y−∂Q/∂z) dy∧dz + (∂P/∂z−∂R/∂x) dz∧dx + (∂Q/∂x−∂P/∂y) dx∧dy
# P,Q,R are callables (x,y,z)->float; returns [A,B,C] coefficients of the 2-form
def ExteriorDerivative1Form(P, Q, R, x, y, z, h=_H):
    def pd(fn,var):
        if   var=='x': return (fn(x+h,y,z)-fn(x-h,y,z))/(2.0*h)
        elif var=='y': return (fn(x,y+h,z)-fn(x,y-h,z))/(2.0*h)
        else:          return (fn(x,y,z+h)-fn(x,y,z-h))/(2.0*h)
    return [pd(R,'y')-pd(Q,'z'), pd(P,'z')-pd(R,'x'), pd(Q,'x')-pd(P,'y')]  # [A,B,C]

# Formula: d(A dy∧dz + B dz∧dx + C dx∧dy) = (∂A/∂x + ∂B/∂y + ∂C/∂z) dx∧dy∧dz
# Returns the scalar coefficient of the resulting 3-form (divergence)
def ExteriorDerivative2Form(A_fn, B_fn, C_fn, x, y, z, h=_H):
    dA=(A_fn(x+h,y,z)-A_fn(x-h,y,z))/(2.0*h)
    dB=(B_fn(x,y+h,z)-B_fn(x,y-h,z))/(2.0*h)
    dC=(C_fn(x,y,z+h)-C_fn(x,y,z-h))/(2.0*h)
    return dA+dB+dC                                            # ∂A/∂x + ∂B/∂y + ∂C/∂z

# Formula: α ∧ β for 1-forms α=[P₁,Q₁,R₁], β=[P₂,Q₂,R₂] (values at a point)
def WedgeProduct1Forms(alpha, beta):
    P1,Q1,R1=alpha; P2,Q2,R2=beta
    return [Q1*R2-R1*Q2, R1*P2-P1*R2, P1*Q2-Q1*P2]           # [dy∧dz, dz∧dx, dx∧dy] coeffs

# Formula: pullback φ*ω under φ:ℝ²→ℝ³
# Returns [coeff of ds, coeff of dt] of the pulled-back 1-form at (s,t)
def PullbackOf1Form(P_fn, Q_fn, R_fn, phi, s, t, h=_H):
    ds=_pu(phi,s,t,h); dt_=_pv(phi,s,t,h); pt=phi(s,t)
    om=[P_fn(*pt), Q_fn(*pt), R_fn(*pt)]
    return [_dot(om,ds), _dot(om,dt_)]                         # Complete pullback

# Formula: ∫_C ω — line integral of 1-form ω = P dx + Q dy + R dz along γ:[a,b]→ℝ³
def LineIntegralOf1Form(P_fn, Q_fn, R_fn, curve, a, b, n=1000):
    h=(b-a)/n; total=0.0
    for i in range(n):
        t=a+(i+0.5)*h; pt=curve(t); vt=_d1(curve,t)
        total+=(P_fn(*pt)*vt[0]+Q_fn(*pt)*vt[1]+R_fn(*pt)*vt[2])*h
    return total                                               # Complete ∫_C ω

# ============================================================
# RIEMANNIAN GEOMETRY
# ============================================================

# Formula: Rᵏₗᵢⱼ = ∂ᵢΓᵏⱼˡ − ∂ⱼΓᵏᵢˡ + ΓᵐⱼˡΓᵏᵢₘ − ΓᵐᵢˡΓᵏⱼₘ — Riemann curvature tensor
# Returns R[k][l][i][j] — 2×2×2×2 array at (u,v)
def RiemannCurvatureTensor(surface, u, v, h=_H):
    G0=ChristoffelSymbols(surface,u,v,h)
    Gup=ChristoffelSymbols(surface,u+h,v,h); Gum=ChristoffelSymbols(surface,u-h,v,h)
    Gvp=ChristoffelSymbols(surface,u,v+h,h); Gvm=ChristoffelSymbols(surface,u,v-h,h)
    dG=[[[(Gup[k][i][j]-Gum[k][i][j])/(2.0*h) for j in range(2)] for i in range(2)] for k in range(2)],\
       [[[(Gvp[k][i][j]-Gvm[k][i][j])/(2.0*h) for j in range(2)] for i in range(2)] for k in range(2)]
    R=[[[[0.0]*2 for _ in range(2)] for _ in range(2)] for _ in range(2)]
    for k in range(2):
        for l in range(2):
            for i in range(2):
                for j in range(2):
                    val=dG[i][k][j][l]-dG[j][k][i][l]
                    for m in range(2):
                        val+=G0[m][j][l]*G0[k][i][m]-G0[m][i][l]*G0[k][j][m]
                    R[k][l][i][j]=val
    return R                                                   # Complete Riemann tensor

# Formula: Rᵢⱼ = Σₖ Rᵏᵢₖⱼ — Ricci tensor (contraction of Riemann)
def RicciTensor(surface, u, v, h=_H):
    R=RiemannCurvatureTensor(surface,u,v,h)
    return [[sum(R[k][i][k][j] for k in range(2)) for j in range(2)] for i in range(2)]

# Formula: R = gⁱʲ Rᵢⱼ — scalar curvature (= 2K for a 2D surface)
def ScalarCurvature(surface, u, v, h=_H):
    E,F,G=FirstFundamentalForm(surface,u,v,h); det=E*G-F*F
    if abs(det)<1e-14: return 0.0
    gi=[[G/det,-F/det],[-F/det,E/det]]; Ric=RicciTensor(surface,u,v,h)
    return sum(gi[i][j]*Ric[i][j] for i in range(2) for j in range(2))  # Complete R = gⁱʲRᵢⱼ

# ============================================================
# SPECIAL SURFACES — CLOSED-FORM RESULTS
# ============================================================

# Sphere of radius r — (θ,φ) ∈ [0,π]×[0,2π)
# Returns (surface_fn, K, H, area) with exact closed-form values
def Sphere(r=1.0):
    def surface(theta,phi):
        return [r*math.sin(theta)*math.cos(phi), r*math.sin(theta)*math.sin(phi), r*math.cos(theta)]
    return surface, 1.0/r**2, 1.0/r, 4.0*math.pi*r**2         # K=1/r², H=1/r, A=4πr²

# Torus with major radius R and tube radius a — (θ,φ) ∈ [0,2π)²
# Returns (surface_fn, K_fn, H_fn, area)
def Torus(R=2.0, a=1.0):
    def surface(theta,phi):
        return [(R+a*math.cos(phi))*math.cos(theta), (R+a*math.cos(phi))*math.sin(theta), a*math.sin(phi)]
    K_fn=lambda t,p: math.cos(p)/(a*(R+a*math.cos(p)))
    H_fn=lambda t,p: (R+2.0*a*math.cos(p))/(2.0*a*(R+a*math.cos(p)))
    return surface, K_fn, H_fn, 4.0*math.pi**2*R*a             # A = 4π²Ra

# Cylinder of radius r — (θ,z)
# Returns (surface_fn, K=0, H=1/(2r))
def Cylinder(r=1.0):
    def surface(theta,z): return [r*math.cos(theta), r*math.sin(theta), z]
    return surface, 0.0, 1.0/(2.0*r)                           # K=0, H=1/(2r)

# Paraboloid z = u²+v² — (u,v) ∈ ℝ²
# Returns (surface_fn, K_fn, H_fn)
def Paraboloid():
    def surface(u,v): return [u, v, u*u+v*v]
    K_fn=lambda u,v: 4.0/(1.0+4.0*u*u+4.0*v*v)**2
    H_fn=lambda u,v: (1.0+2.0*u*u+2.0*v*v)/(1.0+4.0*u*u+4.0*v*v)**1.5
    return surface, K_fn, H_fn

# Saddle z = u²−v² — classic hyperbolic surface
# Returns (surface_fn, K_fn, H_fn)
def Saddle():
    def surface(u,v): return [u, v, u*u-v*v]
    K_fn=lambda u,v: -4.0/(1.0+4.0*u*u+4.0*v*v)**2            # K always negative
    H_fn=lambda u,v: (2.0*u*u-2.0*v*v)/(1.0+4.0*u*u+4.0*v*v)**1.5
    return surface, K_fn, H_fn

# Formula: Gauss-Bonnet — for a closed surface ∫∫ K dA = 2πχ
# Returns (χ_float, χ_nearest_int) from a numerically computed total curvature integral
def GaussBonnetCheck(total_K_integral):
    chi = total_K_integral/(2.0*math.pi)
    return chi, round(chi)                                     # χ = (∫∫K dA) / (2π)