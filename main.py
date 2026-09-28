"""Punto de entrada principal del aplicativo de Depuración y Forma Normal de Chomsky."""

import sys
from fnc.interfaz.ventana_principal import VentanaPrincipal


def main() -> None:
    """Inicia la aplicación con la interfaz gráfica de usuario."""
    app = VentanaPrincipal()
    app.mainloop()


if __name__ == "__main__":
    main()
