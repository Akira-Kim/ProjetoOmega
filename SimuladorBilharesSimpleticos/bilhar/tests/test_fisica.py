"""
Testes unitários da física e das curvas (Fase 2).
Rode com:  PYTHONPATH=. python -m pytest bilhar/tests/ -v
ou simplesmente:  PYTHONPATH=. python bilhar/tests/test_fisica.py
"""

from __future__ import annotations
import numpy as np
import sys
import os

# Garante que o pacote é encontrado quando o script é executado diretamente
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from bilhar.curvas import criar_curva, listar_curvas
from bilhar.core.fisica import refletir_vetor, aplicar_colisao
from bilhar.core.estado import EstadoSimulacao
from bilhar.core.integrador import Integrador


def assert_almost_equal(a, b, tol=1e-8, msg=""):
    if not np.allclose(a, b, atol=tol, rtol=tol):
        raise AssertionError(f"{msg}\n  obtido : {a}\n  esperado: {b}")


def test_curvas_registradas():
    nomes = listar_curvas()
    assert "Círculo" in nomes
    assert "Elipse" in nomes
    assert "Estádio" in nomes
    print("✓ Curvas registradas:", nomes)


def test_circulo_basico():
    c = criar_curva("Círculo")
    p0 = c.ponto(0.0)
    assert_almost_equal(p0, [1.0, 0.0], msg="ponto(0)")
    p_pi2 = c.ponto(np.pi / 2)
    assert_almost_equal(p_pi2, [0.0, 1.0], msg="ponto(π/2)")

    tg = c.tangente(0.0)
    assert_almost_equal(tg, [0.0, 1.0], msg="tangente(0)")

    # Interseção com reta horizontal pelo centro
    lambs = c.intersect_line(np.array([0.0, 0.0]), np.array([1.0, 0.0]))
    assert len(lambs) == 2
    assert_almost_equal(sorted(lambs), [-1.0, 1.0], msg="intersect eixo x")
    print("✓ Círculo básico OK")


def test_elipse_basico():
    e = criar_curva("Elipse", a=2.0, b=1.0)
    p0 = e.ponto(0.0)
    assert_almost_equal(p0, [2.0, 0.0], msg="elipse ponto(0)")
    p_pi2 = e.ponto(np.pi / 2)
    assert_almost_equal(p_pi2, [0.0, 1.0], msg="elipse ponto(π/2)")
    print("✓ Elipse básica OK")


def test_estadio_basico():
    s = criar_curva("Estádio", a=1.0, b=1.0)  # a=semi-reta, b=raio
    # Ponto no meio da reta superior
    # perimetro = 2*2 + 2*π ≈ 4 + 6.28 = 10.28
    # meio da reta superior está em s = 1.0 (a=1 → len_reta=2)
    t_meio_sup = (1.0 / s.perimetro) * 2 * np.pi
    p = s.ponto(t_meio_sup)
    assert_almost_equal(p, [0.0, 1.0], tol=1e-6, msg="meio reta superior")

    # Tangente na reta superior deve ser (1,0)
    tg = s.tangente(t_meio_sup)
    assert_almost_equal(tg, [1.0, 0.0], tol=1e-6, msg="tangente reta superior")
    print("✓ Estádio básico OK")


def test_reflexao_elastica():
    v = np.array([1.0, -1.0])
    n = np.array([0.0, 1.0])  # normal para cima
    v2 = refletir_vetor(v, n)
    assert_almost_equal(v2, [1.0, 1.0], msg="reflexão elástica")
    print("✓ Reflexão elástica OK")


def test_integrador_sem_crash():
    """Roda alguns passos e verifica que o número de colisões aumenta."""
    for nome, params in [
        ("Círculo", {}),
        ("Elipse", {"a": 1.5, "b": 1.0}),
        ("Estádio", {"a": 0.8, "b": 1.0}),
    ]:
        for modo in ["Elástico", "Simplético"]:
            est = EstadoSimulacao(curva_nome=nome, modo=modo, **params)
            est.pausado = False
            integ = Integrador(est)
            n0 = len(est.lista_t_colisao)
            for _ in range(80):
                integ.passo(0.04)
            n1 = len(est.lista_t_colisao)
            assert n1 > n0, f"{nome}/{modo} não gerou colisões"
            # Velocidade não deve explodir
            assert np.linalg.norm(est.vel) < 10.0
    print("✓ Integrador (todas as curvas × 2 modos) OK")


def test_t_from_pos_roundtrip():
    """ponto(t) → t_from_pos deve recuperar t aproximadamente."""
    for nome, params in [
        ("Círculo", {}),
        ("Elipse", {"a": 1.3, "b": 0.7}),
        ("Estádio", {"a": 1.0, "b": 1.0}),
    ]:
        curva = criar_curva(nome, **params)
        for t_orig in np.linspace(0.1, 2 * np.pi - 0.1, 12):
            p = curva.ponto(t_orig)
            t_rec = curva.t_from_pos(p)
            # Diferença angular mínima
            diff = abs((t_rec - t_orig + np.pi) % (2 * np.pi) - np.pi)
            assert diff < 0.15, f"{nome}: t={t_orig:.3f} → recuperado {t_rec:.3f}"
    print("✓ t_from_pos round-trip OK")


if __name__ == "__main__":
    print("Rodando testes da Fase 2...\n")
    test_curvas_registradas()
    test_circulo_basico()
    test_elipse_basico()
    test_estadio_basico()
    test_reflexao_elastica()
    test_t_from_pos_roundtrip()
    test_integrador_sem_crash()
    print("\n✅ Todos os testes passaram.")
