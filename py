import flet as ft
import sqlite3
from datetime import datetime

def init_db():
    conn = sqlite3.connect("ventas.db")
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS ventas 
                      (id INTEGER PRIMARY KEY, lote TEXT, usuario TEXT, 
                       gramos REAL, precio REAL, parcial REAL, fecha TEXT, pactado TEXT)''')
    conn.commit()
    conn.close()

def main(page: ft.Page):
    init_db()
    page.title = "Green Dispenser Pro"
    page.theme_mode = ft.ThemeMode.DARK
    page.scroll = "adaptive"

    txt_lote = ft.TextField(hint_text="Lote", width=80)
    txt_usuario = ft.TextField(hint_text="Usuario", width=120)
    txt_gramos = ft.TextField(hint_text="Gramos", width=90)
    txt_precio = ft.TextField(hint_text="Precio x g", width=100)
    txt_parcial = ft.TextField(hint_text="Parcial", width=100)
    txt_fecha_pactada = ft.TextField(hint_text="Pactado", width=110)
    lista_tarjetas = ft.Column()

    def refrescar(e=None):
        lista_tarjetas.controls.clear()
        conn = sqlite3.connect("ventas.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM ventas ORDER BY id DESC")
        for v in cursor.fetchall():
            # v = (id, lote, usuario, gramos, precio, parcial, fecha, pactado)
            total = v[3] * v[4]
            debe = total - v[5]
            
            # Botón lápiz que edita usando el ID de la base de datos
            def editar_registro(id_reg):
                print(f"Editando ID: {id_reg}")
            
            tarjeta = ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Text(f"Lote: {v[1]} | Usuario: {v[2]}", color="green", weight="bold"),
                        ft.IconButton(icon=ft.icons.EDIT, icon_size=16)
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    ft.Text(f"Gramos: {v[3]} | Total: ${total:.2f}"),
                    ft.Text(f"Parcial: ${v[5]} | Debe: ${debe:.2f}", color="red" if debe > 0 else "green")
                ]),
                border=ft.border.all(1, "white24"), padding=10, border_radius=8
            )
            lista_tarjetas.controls.append(tarjeta)
        conn.close()
        page.update()

    def registrar(e):
        conn = sqlite3.connect("ventas.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO ventas (lote, usuario, gramos, precio, parcial, fecha, pactado) VALUES (?,?,?,?,?,?,?)",
                       (txt_lote.value, txt_usuario.value, float(txt_gramos.value or 0), 
                        float(txt_precio.value or 0), float(txt_parcial.value or 0), 
                        datetime.now().strftime("%d/%m/%Y"), txt_fecha_pactada.value))
        conn.commit()
        conn.close()
        refrescar()

    page.add(
        ft.Text("REGISTRO DE VENTAS", size=18, weight="bold"),
        ft.Row([txt_lote, txt_usuario, txt_gramos, txt_precio, txt_parcial, txt_fecha_pactada], wrap=True),
        ft.ElevatedButton("REGISTRAR", on_click=registrar, bgcolor="green", color="white"),
        lista_tarjetas
    )
    refrescar()

ft.app(target=main)

