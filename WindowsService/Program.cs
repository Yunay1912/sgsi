// Program.cs - Servicio Windows Completo
using Microsoft.AspNetCore.Builder;
using Microsoft.Extensions.DependencyInjection;
using System.Media;
using System.IO;
using Npgsql;
using Newtonsoft.Json;

var builder = WebApplication.CreateBuilder(args);
builder.Services.AddControllers();
builder.Services.AddCors(o => o.AddDefaultPolicy(p => p.AllowAnyOrigin().AllowAnyMethod().AllowAnyHeader()));

var app = builder.Build();
app.UseCors();
app.MapControllers();

Console.WriteLine("🚀 Servicio Windows - Puerto 5555");
app.Run("http://localhost:5555");

// ==================== NOTIFICACIONES ====================
[Microsoft.AspNetCore.Mvc.ApiController]
[Microsoft.AspNetCore.Mvc.Route("api/[controller]")]
public class NotificacionesController : Microsoft.AspNetCore.Mvc.ControllerBase
{
    private static readonly Dictionary<string, SoundPlayer> Sounds = new();
    private static string ConnStr = GetConnectionString();
    
    static NotificacionesController()
    {
        var soundsPath = Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "assets", "sounds");
        foreach (var file in new[] { "reject.wav", "new_boleta.wav", "login_fail.wav" })
        {
            var path = Path.Combine(soundsPath, file);
            if (File.Exists(path))
            {
                Sounds[Path.GetFileNameWithoutExtension(file)] = new SoundPlayer(path);
                Console.WriteLine($"✅ Sonido: {file}");
            }
        }
    }

    [Microsoft.AspNetCore.Mvc.HttpPost("sound")]
    public IActionResult PlaySound([Microsoft.AspNetCore.Mvc.FromBody] SoundRequest req)
    {
        if (Sounds.TryGetValue(req.Key, out var player))
        {
            player.Play();
            Console.WriteLine($"🔊 {req.Key}");
            return Ok();
        }
        return NotFound();
    }

    [Microsoft.AspNetCore.Mvc.HttpPost("toast")]
    public IActionResult ShowToast([Microsoft.AspNetCore.Mvc.FromBody] ToastRequest req)
    {
        try
        {
            new Microsoft.Toolkit.Uwp.Notifications.ToastContentBuilder()
                .AddText(req.Title)
                .AddText(req.Message)
                .Show();
            return Ok();
        }
        catch { return StatusCode(500); }
    }

    // Notificar a operadores y admin
    [Microsoft.AspNetCore.Mvc.HttpPost("notify-operators")]
    public async Task<IActionResult> NotifyOperators([Microsoft.AspNetCore.Mvc.FromBody] NotifyRequest req)
    {
        await using var conn = new NpgsqlConnection(ConnStr);
        await conn.OpenAsync();

        var cmd = new NpgsqlCommand(@"
            SELECT u.extension FROM usuarios u
            JOIN roles r ON u.rol_id = r.id
            WHERE r.nombre IN ('operador', 'admin') AND u.activo = TRUE", conn);

        var extensions = new List<string>();
        await using (var reader = await cmd.ExecuteReaderAsync())
        {
            while (await reader.ReadAsync())
                extensions.Add(reader.GetString(0));
        }

        // Crear notificaciones en BD
        foreach (var ext in extensions)
        {
            var insertCmd = new NpgsqlCommand(@"
                INSERT INTO notificaciones (extension, tipo, numero_boleta, mensaje)
                VALUES (@ext, 'nueva_boleta', @num, @msg)", conn);
            insertCmd.Parameters.AddWithValue("ext", ext);
            insertCmd.Parameters.AddWithValue("num", req.NumeroBoleta);
            insertCmd.Parameters.AddWithValue("msg", req.Mensaje);
            await insertCmd.ExecuteNonQueryAsync();
        }

        // Reproducir sonido
        if (Sounds.TryGetValue("new_boleta", out var player))
            player.Play();

        return Ok(new { notificados = extensions.Count });
    }
}

// ==================== BOLETAS ====================
[Microsoft.AspNetCore.Mvc.ApiController]
[Microsoft.AspNetCore.Mvc.Route("api/[controller]")]
public class BoletasController : Microsoft.AspNetCore.Mvc.ControllerBase
{
    private static string ConnStr = GetConnectionString();

    [Microsoft.AspNetCore.Mvc.HttpPost]
    public async Task<IActionResult> Create([Microsoft.AspNetCore.Mvc.FromBody] BoletaRequest req)
    {
        await using var conn = new NpgsqlConnection(ConnStr);
        await conn.OpenAsync();
        await using var trans = await conn.BeginTransactionAsync();

        try
        {
            var cmd = new NpgsqlCommand(@"
                INSERT INTO boletas (numero_boleta, extension, nombre_usuario, paginas, estado, 
                    servicios, copias_color, copias_bn, total_copias, cantidad_documentos, empaste, 
                    observaciones, fecha_solicitud, dia, meta, creado_por)
                VALUES (@num, @ext, @nom, @pag, 'Pendiente', @serv::jsonb, @cc, @cbn, @tc, @cd, 
                    @emp::jsonb, @obs, now(), @dia, @meta::jsonb, @creado)
                RETURNING id", conn, trans);

            cmd.Parameters.AddWithValue("num", req.NumeroBoleta);
            cmd.Parameters.AddWithValue("ext", req.Extension ?? (object)DBNull.Value);
            cmd.Parameters.AddWithValue("nom", req.NombreUsuario);
            cmd.Parameters.AddWithValue("pag", req.Paginas);
            cmd.Parameters.AddWithValue("serv", JsonConvert.SerializeObject(req.Servicios ?? new()));
            cmd.Parameters.AddWithValue("cc", req.CopiasColor);
            cmd.Parameters.AddWithValue("cbn", req.CopiasBN);
            cmd.Parameters.AddWithValue("tc", req.Paginas);
            cmd.Parameters.AddWithValue("cd", req.CantidadDocumentos);
            cmd.Parameters.AddWithValue("emp", JsonConvert.SerializeObject(req.Empaste ?? new()));
            cmd.Parameters.AddWithValue("obs", req.Observaciones ?? (object)DBNull.Value);
            cmd.Parameters.AddWithValue("dia", req.Dia ?? GetDia());
            cmd.Parameters.AddWithValue("meta", JsonConvert.SerializeObject(req.Meta ?? new()));
            cmd.Parameters.AddWithValue("creado", req.NombreUsuario);

            var id = await cmd.ExecuteScalarAsync();
            await trans.CommitAsync();

            Console.WriteLine($"✅ Boleta {req.NumeroBoleta} - ID={id}");
            return Ok(new { id });
        }
        catch (Exception ex)
        {
            await trans.RollbackAsync();
            Console.WriteLine($"❌ Error: {ex.Message}");
            return StatusCode(500, ex.Message);
        }
    }

    [Microsoft.AspNetCore.Mvc.HttpGet]
    public async Task<IActionResult> List([Microsoft.AspNetCore.Mvc.FromQuery] int limit = 500)
    {
        await using var conn = new NpgsqlConnection(ConnStr);
        await conn.OpenAsync();

        var cmd = new NpgsqlCommand(@"
            SELECT id, numero_boleta, extension, nombre_usuario, paginas, estado, 
                   copias_color, copias_bn, fecha_solicitud, dia, operador_responsable, 
                   cerrado, observaciones
            FROM boletas WHERE estado != 'Rechazado' AND cerrado = FALSE
            ORDER BY fecha_solicitud DESC LIMIT @lim", conn);
        cmd.Parameters.AddWithValue("lim", limit);

        var boletas = new List<object>();
        await using var reader = await cmd.ExecuteReaderAsync();
        while (await reader.ReadAsync())
        {
            boletas.Add(new
            {
                id = reader.GetInt32(0),
                numero_boleta = reader.GetString(1),
                extension = reader.IsDBNull(2) ? null : reader.GetString(2),
                nombre_usuario = reader.GetString(3),
                paginas = reader.GetInt32(4),
                estado = reader.GetString(5),
                copias_color = reader.GetInt32(6),
                copias_bn = reader.GetInt32(7),
                fecha_solicitud = reader.GetDateTime(8),
                dia = reader.IsDBNull(9) ? null : reader.GetString(9),
                operador_responsable = reader.IsDBNull(10) ? null : reader.GetString(10),
                cerrado = reader.GetBoolean(11),
                observaciones = reader.IsDBNull(12) ? null : reader.GetString(12)
            });
        }
        return Ok(boletas);
    }

    [Microsoft.AspNetCore.Mvc.HttpPut("{numero}/estado")]
    public async Task<IActionResult> UpdateEstado(string numero, [Microsoft.AspNetCore.Mvc.FromBody] EstadoUpdate req)
    {
        await using var conn = new NpgsqlConnection(ConnStr);
        await conn.OpenAsync();
        await using var trans = await conn.BeginTransactionAsync();

        try
        {
            string query;
            if (req.Estado.ToLower() == "listo")
            {
                query = @"UPDATE boletas SET estado = @est, fecha_procesado = now(), 
                         operador_responsable = @op, listo_para_cierre = TRUE 
                         WHERE numero_boleta = @num RETURNING id";
            }
            else
            {
                query = @"UPDATE boletas SET estado = @est, operador_responsable = @op 
                         WHERE numero_boleta = @num RETURNING id";
            }

            var cmd = new NpgsqlCommand(query, conn, trans);
            cmd.Parameters.AddWithValue("est", req.Estado);
            cmd.Parameters.AddWithValue("op", req.Operador ?? (object)DBNull.Value);
            cmd.Parameters.AddWithValue("num", numero);

            var result = await cmd.ExecuteScalarAsync();
            await trans.CommitAsync();

            Console.WriteLine($"✅ {numero} → {req.Estado}");
            return result != null ? Ok() : NotFound();
        }
        catch (Exception ex)
        {
            await trans.RollbackAsync();
            return StatusCode(500, ex.Message);
        }
    }

    [Microsoft.AspNetCore.Mvc.HttpDelete("{numero}")]
    public async Task<IActionResult> Delete(string numero)
    {
        await using var conn = new NpgsqlConnection(ConnStr);
        await conn.OpenAsync();
        await using var trans = await conn.BeginTransactionAsync();

        try
        {
            var cmd = new NpgsqlCommand("DELETE FROM boletas WHERE numero_boleta = @num RETURNING id", conn, trans);
            cmd.Parameters.AddWithValue("num", numero);
            var result = await cmd.ExecuteScalarAsync();
            await trans.CommitAsync();

            if (result != null)
            {
                Console.WriteLine($"🗑️ {numero} rechazado");
                // Reproducir sonido
                if (NotificacionesController.Sounds.TryGetValue("reject", out var player))
                    player.Play();
            }

            return result != null ? Ok() : NotFound();
        }
        catch (Exception ex)
        {
            await trans.RollbackAsync();
            return StatusCode(500, ex.Message);
        }
    }

    // Enviar a cierre
    [Microsoft.AspNetCore.Mvc.HttpPost("{numero}/enviar-cierre")]
    public async Task<IActionResult> EnviarCierre(string numero, [Microsoft.AspNetCore.Mvc.FromBody] CierreRequest req)
    {
        await using var conn = new NpgsqlConnection(ConnStr);
        await conn.OpenAsync();
        await using var trans = await conn.BeginTransactionAsync();

        try
        {
            var cmd = new NpgsqlCommand(@"
                UPDATE boletas SET cerrado = TRUE, listo_para_cierre = FALSE, 
                       enviado_cierre_por = @por, fecha_envio_cierre = now()
                WHERE numero_boleta = @num AND estado = 'Listo'
                RETURNING id", conn, trans);
            cmd.Parameters.AddWithValue("num", numero);
            cmd.Parameters.AddWithValue("por", req.EnviadoPor ?? (object)DBNull.Value);

            var result = await cmd.ExecuteScalarAsync();
            await trans.CommitAsync();

            return result != null ? Ok() : NotFound();
        }
        catch (Exception ex)
        {
            await trans.RollbackAsync();
            return StatusCode(500, ex.Message);
        }
    }

    private static string GetDia()
    {
        var dias = new[] { "Domingo", "Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado" };
        return dias[(int)DateTime.Now.DayOfWeek];
    }
}

// ==================== AUDITORÍA ====================
[Microsoft.AspNetCore.Mvc.ApiController]
[Microsoft.AspNetCore.Mvc.Route("api/[controller]")]
public class AuditoriaController : Microsoft.AspNetCore.Mvc.ControllerBase
{
    private static string ConnStr = GetConnectionString();

    [Microsoft.AspNetCore.Mvc.HttpPost]
    public async Task<IActionResult> Registrar([Microsoft.AspNetCore.Mvc.FromBody] AuditoriaRequest req)
    {
        await using var conn = new NpgsqlConnection(ConnStr);
        await conn.OpenAsync();

        var cmd = new NpgsqlCommand(@"
            INSERT INTO auditoria (fecha, extension, accion, detalle)
            VALUES (now(), @ext, @acc, @det) RETURNING id", conn);
        cmd.Parameters.AddWithValue("ext", req.Extension ?? (object)DBNull.Value);
        cmd.Parameters.AddWithValue("acc", req.Accion);
        cmd.Parameters.AddWithValue("det", req.Detalle ?? (object)DBNull.Value);

        var id = await cmd.ExecuteScalarAsync();
        
        // Log solo acciones importantes
        if (req.Accion.Contains("login") || req.Accion.Contains("admin") || req.Accion.Contains("control"))
            Console.WriteLine($"📋 Auditoría: {req.Accion} - {req.Extension}");

        return Ok(new { id });
    }
}

// ==================== USUARIOS ====================
[Microsoft.AspNetCore.Mvc.ApiController]
[Microsoft.AspNetCore.Mvc.Route("api/[controller]")]
public class UsuariosController : Microsoft.AspNetCore.Mvc.ControllerBase
{
    private static string ConnStr = GetConnectionString();

    [Microsoft.AspNetCore.Mvc.HttpPost("login")]
    public async Task<IActionResult> Login([Microsoft.AspNetCore.Mvc.FromBody] LoginRequest req)
    {
        await using var conn = new NpgsqlConnection(ConnStr);
        await conn.OpenAsync();

        var cmd = new NpgsqlCommand(@"
            SELECT u.id, u.usuario, u.nombre_completo, u.extension, u.rol_id, r.nombre as rol
            FROM usuarios u
            LEFT JOIN roles r ON r.id = u.rol_id
            WHERE u.usuario = @user AND u.activo = TRUE
              AND (u.password = @pass OR u.password = crypt(@pass, u.password))
            LIMIT 1", conn);
        
        cmd.Parameters.AddWithValue("user", req.Usuario);
        cmd.Parameters.AddWithValue("pass", req.Password);

        await using var reader = await cmd.ExecuteReaderAsync();
        if (await reader.ReadAsync())
        {
            var user = new
            {
                id = reader.GetInt32(0),
                usuario = reader.GetString(1),
                nombre_completo = reader.GetString(2),
                extension = reader.IsDBNull(3) ? null : reader.GetString(3),
                rol_id = reader.GetInt32(4),
                rol = reader.IsDBNull(5) ? "usuario" : reader.GetString(5)
            };

            Console.WriteLine($"✅ Login: {user.usuario} ({user.rol})");
            return Ok(user);
        }

        return Unauthorized();
    }
}

// ==================== DTOs ====================
public record SoundRequest(string Key);
public record ToastRequest(string Title, string Message);
public record NotifyRequest(string NumeroBoleta, string Mensaje);
public record BoletaRequest(string NumeroBoleta, string Extension, string NombreUsuario, 
    int Paginas, Dictionary<string, object> Servicios, int CopiasColor, int CopiasBN, 
    int CantidadDocumentos, Dictionary<string, object> Empaste, string Observaciones, 
    string Dia, Dictionary<string, object> Meta);
public record EstadoUpdate(string Estado, string Operador);
public record CierreRequest(string EnviadoPor);
public record AuditoriaRequest(string Extension, string Accion, string Detalle);
public record LoginRequest(string Usuario, string Password);

// Helper
static string GetConnectionString()
{
    return Environment.GetEnvironmentVariable("DATABASE_URL") 
        ?? "Host=localhost;Port=5432;Database=asamblea_db;Username=postgres;Password=yunaykelastuadev";
}