@echo off
echo.
echo ============================================
echo   LUM-PE -- Subida a GitHub
echo   github.com/julespintor-tech/lum-pe
echo ============================================
echo.

:: Configurar nombre y email de git (global)
git config --global user.name "Julio David Rojas Aguayo"
git config --global user.email "jules_pintor@outlook.com"

:: Inicializar repo
echo [1/5] Inicializando repositorio...
git init

:: Agregar todos los archivos
echo [2/5] Agregando archivos...
git add .

:: Primer commit
echo [3/5] Creando commit...
git commit -m "feat: LUM-PE v0.1.0 -- initial public release (vO.2026-02)"

:: Configurar rama main
echo [4/5] Configurando rama main...
git branch -M main

:: Conectar con GitHub y subir
echo [5/5] Subiendo a GitHub...
echo.
echo NOTA: Se abrira una ventana para autenticarte con GitHub.
echo Usa tu usuario: julespintor-tech
echo.
git remote add origin https://github.com/julespintor-tech/lum-pe.git
git push -u origin main

echo.
echo ============================================
echo   LISTO! Revisa github.com/julespintor-tech/lum-pe
echo ============================================
echo.
pause
