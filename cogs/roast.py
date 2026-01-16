import random
import json
import os
import discord
from discord.ext import commands  # <- esto es clave
from discord.ext.commands import cooldown, BucketType, cooldown
from config import (
    MODO_POR_DEFECTO,
    COOLDOWN_INSULTAME,
    COOLDOWN_ROAST
)

NIVELES = {
    5: "🍼 {user} ya no llora con el primer insulto.",
    10: "🧠 {user} empieza a desarrollar tolerancia al sarcasmo.",
    20: "🔥 {user} ya se ríe del dolor.",
    30: "💀 {user} ha perdido toda esperanza… y le gusta.",
    50: "👑 {user} es oficialmente inmune a la dignidad."
}

class Roast(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.roasts = self.cargar_roasts()
        self.frases = self.cargar_frases()
        self.servidores = self.cargar_servidores()
        self.reputacion = self.cargar_reputacion()

    def cargar_roasts(self):
        ruta = os.path.join("data", "roasts.json")
        with open(ruta, "r", encoding="utf-8") as f:
            return json.load(f)
        
    def cargar_config(self):
        ruta = os.path.join("data", "server_config.json")
        if not os.path.exists(ruta):
            return {}
        with open(ruta, "r", encoding="utf-8") as f:
            return json.load(f)

    def guardar_config(self):
        ruta = os.path.join("data", "server_config.json")
        with open(ruta, "w", encoding="utf-8") as f:
            json.dump(self.server_config, f, indent=4)

    def obtener_modo(self, guild_id):
        guild_id = str(guild_id)

        if guild_id not in self.server_config:
            self.server_config[guild_id] = {
                "modo": MODO_POR_DEFECTO
            }
            self.guardar_config()

        return self.server_config[guild_id]["modo"]
    
    def cargar_servidores(self):
        ruta = os.path.join("data", "servers.json")
        if not os.path.exists(ruta):
            return {}
        with open(ruta, "r", encoding="utf-8") as f:
            return json.load(f)
    
    def guardar_servidores(self):
        ruta = os.path.join("data", "servers.json")
        with open(ruta, "w", encoding="utf-8") as f:
            json.dump(self.servidores, f, indent=4)
    
    def asegurar_servidor(self, guild_id):
        gid = str(guild_id)

        if gid not in self.servidores:
            self.servidores[gid] = {
             "modo": MODO_POR_DEFECTO,
                "blacklist": []
            }
            self.guardar_servidores()

        return self.servidores[gid]


    # ---------------- EVENTO ----------------
    @commands.Cog.listener()
    async def on_ready(self):
        print("🔥 Cog Roast cargado")

    # ---------------- COMANDOS ----------------
    @commands.command()
    async def modos(self, ctx):
        servidor = self.asegurar_servidor(ctx.guild.id)
        modo_actual = servidor["modo"]

        modos_disponibles = ", ".join(self.roasts.keys())

        await ctx.send(
            f"🎭 **Modos disponibles:** {modos_disponibles}\n"
            f"👉 Modo actual en este servidor: **{modo_actual}**"
    )

    @commands.command()
    async def modo(self, ctx, nuevo_modo: str):
        servidor = self.asegurar_servidor(ctx.guild.id)
        nuevo_modo = nuevo_modo.lower()

        if nuevo_modo not in self.roasts:
            modos_disponibles = ", ".join(self.roasts.keys())
            await ctx.send(
                f"❌ Modo desconocido.\n"
                f"Modos disponibles: {modos_disponibles}"
            )
            return

        servidor["modo"] = nuevo_modo
        self.guardar_servidores()

        await ctx.send(
            f"🎭 Modo cambiado a **{nuevo_modo}** para este servidor."
        )

    @commands.command()
    @cooldown(1, COOLDOWN_INSULTAME, BucketType.user)
    async def insultame(self, ctx):
        servidor = self.asegurar_servidor(ctx.guild.id)
        modo = servidor["modo"]

        accion = random.choices(
            ["insultar", "pasar", "comentario"],
            weights=[70, 15, 15],
            k=1
        )[0]

        if accion == "pasar":
            frase = random.choice(self.frases["pasar"])
            await ctx.send(frase)
            return

        if accion == "comentario":
            frase = random.choice(self.frases["comentario"])
            await ctx.send(frase)
            return

        insulto = random.choice(self.roasts[modo])
        await ctx.send(f"{ctx.author.mention}, {insulto}")

        await self.sumar_punto(ctx, ctx.author.id)

    @commands.command()
    @cooldown(1, COOLDOWN_ROAST, BucketType.user)
    async def roast(self, ctx, miembro: discord.Member = None):
        # Evitar DMs
        if ctx.guild is None:
            await ctx.send("Aquí no insulto en privado. Transparencia ante todo.")
            return

        # Validar mención
        if miembro is None:
            await ctx.send("Tienes que mencionar a alguien. No leo mentes (aún).")
            return

        servidor = self.asegurar_servidor(ctx.guild.id)
        uid = str(miembro.id)

        # Comprobar blacklist
        if uid in servidor["blacklist"]:
            await ctx.send(
                f"No puedo insultar a {miembro.mention}. "
                f"Ha activado el escudo de dignidad."
            )
            return

        modo = servidor["modo"]
        insulto = random.choice(self.roasts[modo])

        await ctx.send(f"{miembro.mention}, {insulto} ")
        
    @commands.command(name="noroast")
    async def no_roast(self, ctx, miembro: discord.Member = None):
        if miembro is None:
            await ctx.send("Tienes que decir a quién quieres proteger 👀")
            return
        
        servidor = self.asegurar_servidor(ctx.guild.id)
        uid = str(ctx.author.id)

        if uid not in servidor["blacklist"]:
            servidor["blacklist"].append(uid)
            self.guardar_servidores()
            frase = random.choice(self.frases["denegado"])
            await ctx.send(f"{frase} {miembro.mention} 😇")
        else:
            await ctx.send(f"{miembro.mention} ya estaba a salvo. Más protección que eso, imposible.")

    @commands.command(name="roastme")
    async def roastme(self, ctx):
        servidor = self.asegurar_servidor(ctx.guild.id)
        uid = str(ctx.author.id)

        if uid in servidor["blacklist"]:
            servidor["blacklist"].remove(uid)
            self.guardar_servidores()
            await ctx.send("Has vuelto. El sarcasmo te echaba de menos.")
        else:
            await ctx.send("Nunca te fuiste. El peligro eras tú.")
    
    def cargar_frases(self):
        ruta = os.path.join("data", "frases.json")
        with open(ruta, "r", encoding="utf-8") as f:
            return json.load(f)
    
    async def sumar_punto(self, ctx, user_id):
        uid = str(user_id)

        if uid not in self.reputacion["usuarios"]:
            self.reputacion["usuarios"][uid] = {
                "puntos": 0,
                "niveles": []
            }

        usuario = self.reputacion["usuarios"][uid]
        usuario["puntos"] += 1

        puntos = usuario["puntos"]

        for nivel, mensaje in NIVELES.items():
            if puntos >= nivel and nivel not in usuario["niveles"]:
                usuario["niveles"].append(nivel)
                await ctx.send(
                    mensaje.format(user=ctx.author.mention)
                )

        self.guardar_reputacion()
    
    @commands.command()
    async def nivel(self, ctx, miembro: discord.Member = None):
        user = miembro or ctx.author
        uid = str(user.id)

        datos = self.reputacion["usuarios"].get(uid, {"puntos": 0})
        puntos = datos.get("puntos", 0)

        titulo = self.obtener_titulo(puntos)
        prox = self.siguiente_nivel(puntos)

        mensaje = (
            f"**{user.display_name}**\n"
            f"{titulo}\n"
            f"🔥 Puntos: **{puntos}**\n"
        )

        if prox:
            mensaje += f"🏅 Próximo nivel: **{prox}**"
        else:
            mensaje += "🏅 Nivel máximo alcanzado"

        await ctx.send(mensaje)

    @commands.command()
    async def ranking(self, ctx):
        ranking = sorted(
            self.reputacion["usuarios"].items(),
            key=lambda x: x[1]["puntos"],
            reverse=True
        )[:5]

        mensaje = "🏆 **Ranking de resistencia emocional** 🏆\n"

        for i, (uid, data) in enumerate(ranking, start=1):
            user = ctx.guild.get_member(int(uid))
            if user:
                mensaje += f"{i}. {user.display_name} — {data['puntos']} puntos\n"

        await ctx.send(mensaje)
    
    def obtener_titulo(self, puntos):
        if puntos >= 50:
            return "👑 Leyenda del sarcasmo"
        elif puntos >= 30:
            return "💀 Sin alma"
        elif puntos >= 20:
            return "🔥 Resistente"
        elif puntos >= 10:
            return "🧠 Adaptado al sarcasmo"
        elif puntos >= 5:
            return "🍼 Novato"
        else:
            return "🙂 Inocente"
        
    def siguiente_nivel(self, puntos):
        niveles = [5, 10, 20, 30, 50]
        for nivel in niveles:
            if puntos < nivel:
                return nivel
        return None
        
    def cargar_reputacion(self):
        if not os.path.exists("data/reputacion.json"):
            return {"usuarios": {}}

        with open("data/reputacion.json", "r", encoding="utf-8") as f:
            return json.load(f)
    
    def guardar_reputacion(self):
        with open("data/reputacion.json", "w", encoding="utf-8") as f:
            json.dump(self.reputacion, f, indent=4, ensure_ascii=False)

    # ---------------- ERRORES ----------------
    @insultame.error
    @roast.error
    async def cooldown_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.send("⏳ Tranquilo… ni yo soy tan pesado.")

# ---------------- SETUP ----------------
async def setup(bot):
    await bot.add_cog(Roast(bot))
