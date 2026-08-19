import flet as ft
import sqlite3
from datetime import datetime

def main(page: ft.Page):
    # --- 🌿 ESTILO BOTÁNICO ÁCIDO Y GORDO ---
    page.title = "Green Dispenser"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = "#010a01" # Fondo verde ultra oscuro
    page.padding = 20
    page.scroll = "adaptive"

    def get_conn():
        conn = sqlite3.connect("ventas.db")
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ventas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fecha TEXT, lote TEXT, usuario TEXT, gramos REAL, 
                precio_gramo REAL, parcial REAL, pactado TEXT
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS lotes_stock (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                lote TEXT, 
                gramos_entran REAL,
                precio_gramo REAL,
                deuda REAL,
                entrega REAL
            )
        """)
        conn.commit()
        return conn

    edit_venta_id = [None]

    # --- ESTÉTICA INPUTS ÁCIDOS ---
    bg_in = "#031403"      
    col_in = "#ccff00"     
    brd_in = "#39ff14"     

    # --- 1. INGRESO DE LOTE (CON AUTO-CÁLCULO TOTAL Y DEUDA) ---
    txt_l_lote = ft.TextField(label="Número de Lote", width=120, bgcolor=bg_in, color=col_in, border_color=brd_in, text_style=ft.TextStyle(weight="bold"))
    txt_l_gramos = ft.TextField(label="Gramos del lote", width=140, keyboard_type=ft.KeyboardType.NUMBER, bgcolor=bg_in, color=col_in, border_color=brd_in, text_style=ft.TextStyle(weight="bold"))
    txt_l_precio = ft.TextField(label="Precio/Gramo lote", width=140, keyboard_type=ft.KeyboardType.NUMBER, bgcolor=bg_in, color=col_in, border_color=brd_in, text_style=ft.TextStyle(weight="bold"))
    
    txt_l_total = ft.TextField(label="TOTAL LOTE", width=130, read_only=True, bgcolor="#1a2e1a", color="#ccff00", border_color="#ccff00", text_style=ft.TextStyle(weight="black", size=15))
    txt_l_entrega = ft.TextField(label="Entrega Lote", width=130, keyboard_type=ft.KeyboardType.NUMBER, bgcolor=bg_in, color=col_in, border_color=brd_in)
    txt_l_deuda = ft.TextField(label="Deuda Lote", width=130, read_only=True, bgcolor="#330011", color="#ff0055", border_color="#ff0055", text_style=ft.TextStyle(weight="black", size=15))

    # --- 2. RETIRO DE USUARIO ---
    txt_r_fecha = ft.TextField(label="Fecha", value=datetime.now().strftime("%d/%m/%Y"), width=110, bgcolor=bg_in, color=col_in, border_color=brd_in)
    txt_r_lote = ft.TextField(label="Lote", width=90, bgcolor=bg_in, color=col_in, border_color=brd_in)
    txt_r_usuario = ft.TextField(label="Usuario", width=130, bgcolor=bg_in, color=col_in, border_color=brd_in)
    txt_r_gramos = ft.TextField(label="Gramos", width=90, keyboard_type=ft.KeyboardType.NUMBER, bgcolor=bg_in, color=col_in, border_color=brd_in)
    txt_r_precio = ft.TextField(label="Precio/Gramo", width=120, keyboard_type=ft.KeyboardType.NUMBER, bgcolor=bg_in, color=col_in, border_color=brd_in)
    txt_r_parcial = ft.TextField(label="Entrega Parcial", width=130, keyboard_type=ft.KeyboardType.NUMBER, bgcolor=bg_in, color=col_in, border_color=brd_in)
    txt_r_pactado = ft.TextField(label="Fecha Cancela", width=130, bgcolor=bg_in, color=col_in, border_color=brd_in)

    # Campos auto-calculados de Retiro (Solo lectura)
    txt_r_total = ft.TextField(label="TOTAL", width=120, read_only=True, bgcolor="#1a2e1a", color="#ccff00", border_color="#ccff00", text_style=ft.TextStyle(weight="black", size=16))
    txt_r_debe = ft.TextField(label="DEBE", width=120, read_only=True, bgcolor="#330011", color="#ff0055", border_color="#ff0055", text_style=ft.TextStyle(weight="black", size=16))

    btn_registrar_retiro = ft.ElevatedButton("GUARDAR RETIRO", color="black", bgcolor="#ccff00", style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=4)))

    # --- LÓGICA AUTO-CÁLCULO RETIROS ---
    def calcular_valores(e):
        try:
            g = float(txt_r_gramos.value or 0)
            p = float(txt_r_precio.value or 0)
            parc = float(txt_r_parcial.value or 0)
            tot = g * p
            deb = tot - parc
            txt_r_total.value = f"{tot:.2f}"
            txt_r_debe.value = f"{deb:.2f}"
            page.update()
        except ValueError:
            pass

    txt_r_gramos.on_change = calcular_valores
    txt_r_precio.on_change = calcular_valores
    txt_r_parcial.on_change = calcular_valores

    # --- LÓGICA AUTO-CÁLCULO LOTES ---
    def calcular_valores_lote(e):
        try:
            g = float(txt_l_gramos.value or 0)
            p = float(txt_l_precio.value or 0)
            ent = float(txt_l_entrega.value or 0)
            tot = g * p
            deb = tot - ent
            txt_l_total.value = f"{tot:.2f}"
            txt_l_deuda.value = f"{deb:.2f}"
            page.update()
        except ValueError:
            pass

    txt_l_gramos.on_change = calcular_valores_lote
    txt_l_precio.on_change = calcular_valores_lote
    txt_l_entrega.on_change = calcular_valores_lote

    # --- CONTENEDORES ---
    fila_resumen_lotes = ft.Row(wrap=True, spacing=15)
    
    tabla_excel = ft.DataTable(
        bgcolor="#020a02",
        heading_row_color="#0a1f0a",
        heading_text_style=ft.TextStyle(color="#ccff00", weight="black", size=14),
        data_text_style=ft.TextStyle(color="white", size=13),
        column_spacing=25, 
        columns=[
            ft.DataColumn(ft.Text("")), 
            ft.DataColumn(ft.Text("FECHA")),
            ft.DataColumn(ft.Text("LOTE")),
            ft.DataColumn(ft.Text("USUARIO")),
            ft.DataColumn(ft.Text("GRAMOS")),
            ft.DataColumn(ft.Text("PRECIO")),
            ft.DataColumn(ft.Text("TOTAL")),
            ft.DataColumn(ft.Text("PARCIAL")),
            ft.DataColumn(ft.Text("DEUDA")),
            ft.DataColumn(ft.Text("CANCELA")),
            ft.DataColumn(ft.Text("GANANCIA NETA")),
        ],
        rows=[]
    )

    def borrar_retiro(id_venta):
        conn = get_conn()
        conn.execute("DELETE FROM ventas WHERE id=?", (id_venta,))
        conn.commit()
        conn.close()
        refrescar()

    def borrar_lote(lote_nombre):
        conn = get_conn()
        conn.execute("DELETE FROM lotes_stock WHERE lote=?", (lote_nombre,))
        conn.commit()
        conn.close()
        refrescar()

    def editar_retiro(row_data):
        edit_venta_id[0] = row_data[0]
        txt_r_fecha.value = row_data[1]
        txt_r_lote.value = row_data[2]
        txt_r_usuario.value = row_data[3]
        txt_r_gramos.value = str(row_data[4])
        txt_r_precio.value = str(row_data[5])
        txt_r_parcial.value = str(row_data[6])
        txt_r_pactado.value = row_data[7]
        calcular_valores(None)
        btn_registrar_retiro.text = "ACTUALIZAR RETIRO"
        btn_registrar_retiro.bgcolor = "#ffea00"
        page.update()

    def refrescar():
        tabla_excel.rows.clear()
        fila_resumen_lotes.controls.clear()
        
        conn = get_conn()
        cursor = conn.cursor()
        
        cursor.execute("SELECT lote, precio_gramo FROM lotes_stock")
        costos_lotes = {str(row[0]): float(row[1] or 0) for row in cursor.fetchall()}
        
        cursor.execute("SELECT id, fecha, lote, usuario, gramos, precio_gramo, parcial, pactado FROM ventas ORDER BY id DESC")
        ventas_db = cursor.fetchall()
        
        for v in ventas_db:
            lote_id = str(v[2])
            g = float(v[4] or 0)
            p_venta = float(v[5] or 0)
            total = g * p_venta
            parcial = float(v[6] or 0)
            debe = total - parcial
            
            p_costo = costos_lotes.get(lote_id, 0)
            if p_costo > 0:
                ganancia_neta = (p_venta - p_costo) * g
            else:
                ganancia_neta = total 

            color_deuda = "#ff0055" if debe > 0 else "#ccff00"
            color_ganancia = "#39ff14" if ganancia_neta > 0 else "white"

            tabla_excel.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Row([
                            ft.TextButton(content=ft.Text("✏️", size=14), on_click=lambda e, data=v: editar_retiro(data)),
                            ft.TextButton(content=ft.Text("🗑️", size=14), on_click=lambda e, rid=v[0]: borrar_retiro(rid))
                        ], spacing=0)),
                        ft.DataCell(ft.Text(str(v[1]))), 
                        ft.DataCell(ft.Text(lote_id, weight="black", color="#ccff00")), 
                        ft.DataCell(ft.Text(str(v[3]))), 
                        ft.DataCell(ft.Text(f"{g}g")), 
                        ft.DataCell(ft.Text(f"${p_venta:.2f}")),
                        ft.DataCell(ft.Text(f"${total:.2f}", color="#ccff00", weight="bold")), 
                        ft.DataCell(ft.Text(f"${parcial:.2f}")), 
                        ft.DataCell(ft.Text(f"${debe:.2f}", color=color_deuda, weight="black")), 
                        ft.DataCell(ft.Text(str(v[7]))), 
                        ft.DataCell(ft.Text(f"${ganancia_neta:.2f}", color=color_ganancia, weight="bold")), 
                    ]
                )
            )

        cursor.execute("SELECT lote, SUM(gramos_entran), SUM(deuda), SUM(entrega), SUM(gramos_entran * precio_gramo) FROM lotes_stock GROUP BY lote")
        stock_data = {str(row[0]): {"gramos": row[1] or 0, "deuda": row[2] or 0, "entrega": row[3] or 0, "total_lote": row[4] or 0} for row in cursor.fetchall()}
        
        cursor.execute("SELECT lote, SUM(gramos) FROM ventas GROUP BY lote")
        ventas_resumen = cursor.fetchall()

        lotes_totales = set(list(stock_data.keys()) + [str(r[0]) for r in ventas_resumen if r[0]])
        
        for lote_nombre in sorted(list(lotes_totales)):
            datos_lote = stock_data.get(lote_nombre, {"gramos": 0, "deuda": 0, "entrega": 0, "total_lote": 0})
            entran = datos_lote["gramos"]
            total_lote = datos_lote["total_lote"]
            entrega_l = datos_lote["entrega"]
            deuda_l = total_lote - entrega_l # Automático: si no hay entrega, la deuda es el total del lote

            vendidos_data = next((item for item in ventas_resumen if str(item[0]) == lote_nombre), (lote_nombre, 0))
            vendidos = vendidos_data[1] or 0
            
            stock_actual = entran - vendidos
            
            card_lote = ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Text(f"LOTE {lote_nombre}", weight="black", size=20, color="#ccff00"),
                        ft.Row([
                            ft.Text("🍃", size=18),
                            ft.TextButton(content=ft.Text("🗑️", size=13), on_click=lambda e, ln=lote_nombre: borrar_lote(ln))
                        ], spacing=0)
                    ], alignment="spaceBetween"),
                    ft.Divider(color="#1a2e1a"),
                    ft.Text(f"📥 Ingresaron: {entran:.1f}g", size=14, color="white"),
                    ft.Text(f"📤 Retirados: {vendidos:.1f}g", size=14, color="white"),
                    ft.Text(f"⚖️ STOCK ACTUAL: {stock_actual:.1f}g", size=16, color="#ccff00", weight="black"),
                    ft.Divider(color="#1a2e1a"),
                    ft.Text(f"💎 Total Lote: ${total_lote:.2f}", size=13, color="#ccff00", weight="bold"),
                    ft.Text(f"🤝 Entrega: ${entrega_l:.2f}", size=13, color="#39ff14", weight="bold"),
                    ft.Text(f"💸 Deuda Lote: ${deuda_l:.2f}", size=13, color="#ff0055", weight="bold"),
                ], spacing=4),
                width=260, 
                padding=15, 
                bgcolor="#051405", 
                border_radius=8, 
                border=ft.border.Border(
                    top=ft.border.BorderSide(2, "#ccff00"),
                    right=ft.border.BorderSide(2, "#ccff00"),
                    bottom=ft.border.BorderSide(2, "#ccff00"),
                    left=ft.border.BorderSide(2, "#ccff00")
                )
            )
            fila_resumen_lotes.controls.append(card_lote)

        conn.close()
        page.update()

    def guardar_lote(e):
        try:
            g = float(txt_l_gramos.value or 0)
            p = float(txt_l_precio.value or 0)
            ent = float(txt_l_entrega.value or 0)
            tot = g * p
            deb = tot - ent
            
            conn = get_conn()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO lotes_stock (lote, gramos_entran, precio_gramo, deuda, entrega) VALUES (?,?,?,?,?)",
                           (txt_l_lote.value, g, p, deb, ent))
            conn.commit()
            conn.close()
            
            for txt in [txt_l_lote, txt_l_gramos, txt_l_precio, txt_l_deuda, txt_l_entrega, txt_l_total]:
                txt.value = ""
            refrescar()
        except ValueError:
            pass

    def guardar_retiro(e):
        conn = get_conn()
        cursor = conn.cursor()
        g = float(txt_r_gramos.value or 0)
        p = float(txt_r_precio.value or 0)
        parc = float(txt_r_parcial.value or 0)
        
        if edit_venta_id[0] is None:
            cursor.execute("""
                INSERT INTO ventas (fecha, lote, usuario, gramos, precio_gramo, parcial, pactado) 
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (txt_r_fecha.value, txt_r_lote.value, txt_r_usuario.value, g, p, parc, txt_r_pactado.value))
        else:
            cursor.execute("""
                UPDATE ventas SET fecha=?, lote=?, usuario=?, gramos=?, precio_gramo=?, parcial=?, pactado=? WHERE id=?
            """, (txt_r_fecha.value, txt_r_lote.value, txt_r_usuario.value, g, p, parc, txt_r_pactado.value, edit_venta_id[0]))
            edit_venta_id[0] = None 
            btn_registrar_retiro.text = "GUARDAR RETIRO"
            btn_registrar_retiro.bgcolor = "#ccff00"
            
        conn.commit()
        conn.close()

        for txt in [txt_r_lote, txt_r_usuario, txt_r_gramos, txt_r_precio, txt_r_total, txt_r_parcial, txt_r_debe, txt_r_pactado]:
            txt.value = ""
        refrescar()

    btn_registrar_retiro.on_click = guardar_retiro

    # --- ESTRUCTURA DE LA PÁGINA ---
    page.add(
        
        # LOGO TIPOGRÁFICO
        ft.Container(
            content=ft.Column([
                ft.Text("G D", size=75, weight="w900", color="#001a00", font_family="Impact", italic=True),
                ft.Text("GREEN DISPENSER", size=16, weight="bold", color="#ccff00")
            ], spacing=0, alignment="center")
        ),
        ft.Container(height=20),
        
        ft.Text("RETIRO DE USUARIO", color="#ccff00", weight="black", size=22),
        
        # FICHA DE RETIRO
        ft.Container(
            content=ft.Column([
                ft.Row([txt_r_fecha, txt_r_lote, txt_r_usuario], wrap=True),
                ft.Row([txt_r_gramos, txt_r_precio, txt_r_total], wrap=True),
                ft.Row([txt_r_parcial, txt_r_debe, txt_r_pactado], wrap=True),
                btn_registrar_retiro
            ]), 
            padding=20, 
            bgcolor="#041204", 
            border_radius=8, 
            border=ft.border.Border(
                top=ft.border.BorderSide(1, "#39ff14"),
                right=ft.border.BorderSide(1, "#39ff14"),
                bottom=ft.border.BorderSide(1, "#39ff14"),
                left=ft.border.BorderSide(1, "#39ff14")
            )
        ),
        
        ft.Container(height=15),
        
        # CARGA DE LOTE CON AUTO-CÁLCULO
        ft.Container(
            content=ft.Column([
                ft.Text("🪴 REGISTRAR LOTE NUEVO", color="#ccff00", weight="black", size=18),
                ft.Row([txt_l_lote, txt_l_gramos, txt_l_precio], wrap=True),
                ft.Row([txt_l_total, txt_l_entrega, txt_l_deuda, ft.ElevatedButton("AGREGAR LOTE", color="black", bgcolor="#ccff00", on_click=guardar_lote)], alignment="start", wrap=True)
            ]), padding=15, bgcolor="#041204", border_radius=8
        ),

        ft.Container(height=15),
        ft.Text("📊 STOCK EN TIEMPO REAL", color="#ccff00", weight="black", size=20),
        fila_resumen_lotes,
        
        ft.Container(height=15), 
        ft.Text("📋 PLANILLA HISTÓRICA", color="#ccff00", weight="black", size=20),
        ft.Row([tabla_excel], scroll="always") 
    )

    refrescar()

ft.run(main, view=ft.AppView.WEB_BROWSER)