-- Seed data: Sistema de Estacionamiento Tarifado
-- Compatible con PostgreSQL + SQLAlchemy (ENUM: estadoespacio)
-- Ejecutar una vez que las tablas estén creadas (app.main las crea automáticamente).

INSERT INTO calles (nombre) VALUES
    ('Av. Corrientes'),
    ('Calle San Martín'),
    ('Pasaje del Parque'),
    ('Av. Independencia'),
    ('Calle 25 de Mayo');

INSERT INTO espacios (numero, calle_id, duracion_min_hs, duracion_max_hs, estado) VALUES
    -- Av. Corrientes (id=1)
    (1,  1, 1, 4,  'disponible'),
    (2,  1, 1, 4,  'disponible'),
    (3,  1, 2, 12, 'disponible'),
    (4,  1, 1, 4,  'inhabilitado'),
    (5,  1, 1, 24, 'ocupado'),
    -- Calle San Martín (id=2)
    (1,  2, 1, 8,  'disponible'),
    (2,  2, 1, 8,  'disponible'),
    (3,  2, 1, 8,  'inhabilitado'),
    (4,  2, 1, 8,  'disponible'),
    (5,  2, 1, 8,  'disponible'),
    -- Pasaje del Parque (id=3)
    (1,  3, 1, 4,  'disponible'),
    (2,  3, 1, 4,  'disponible'),
    (3,  3, 1, 4,  'disponible'),
    -- Av. Independencia (id=4)
    (1,  4, 1, 12, 'disponible'),
    (2,  4, 1, 12, 'disponible'),
    (3,  4, 1, 12, 'ocupado'),
    (4,  4, 1, 12, 'disponible'),
    -- Calle 25 de Mayo (id=5)
    (1,  5, 2, 24, 'disponible'),
    (2,  5, 2, 24, 'disponible');

INSERT INTO ocupaciones (espacio_id, chapa, inicio_reserva, duracion_prevista_hs, fin_real) VALUES
    -- Activas (fin_real IS NULL)
    (5,  'ABC123', NOW() - INTERVAL '2 hours', 4, NULL),
    (16, 'AD432FE', NOW() - INTERVAL '1 hour', 3, NULL),

    -- Finalizadas (fin_real IS NOT NULL)
    (1,  'GHI789', NOW() - INTERVAL '1 day',
         2, NOW() - INTERVAL '23 hours'),
    (2,  'JKL012', NOW() - INTERVAL '2 days',
         3, NOW() - INTERVAL '2 days' + INTERVAL '3 hours'),
    (6,  'MNO345', NOW() - INTERVAL '3 days',
         1, NOW() - INTERVAL '3 days' + INTERVAL '1 hour'),
    (11, 'PQ678RS', NOW() - INTERVAL '5 days',
         2, NOW() - INTERVAL '5 days' + INTERVAL '2 hours'),

    -- Futura (reserva programada)
    (1,  'ST901UV', NOW() + INTERVAL '2 days', 4, NULL);
