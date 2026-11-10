CREATE TABLE pacientes (
  id SERIAL PRIMARY KEY,
  documento VARCHAR(20) UNIQUE NOT NULL,
  nombre VARCHAR(120) NOT NULL,
  fecha_nacimiento DATE NOT NULL,
  telefono VARCHAR(20),
  municipio VARCHAR(80),
  regimen VARCHAR(20) NOT NULL -- contributivo | subsidiado | particular
);

CREATE TABLE medicos (
  id SERIAL PRIMARY KEY,
  nombre VARCHAR(120) NOT NULL,
  especialidad VARCHAR(80) NOT NULL
);

CREATE TABLE citas (
  id SERIAL PRIMARY KEY,
  paciente_id INT NOT NULL REFERENCES pacientes(id),
  medico_id INT NOT NULL REFERENCES medicos(id),
  fecha_hora TIMESTAMP NOT NULL,
  motivo TEXT,
  -- Solo cambia al cancelar o reprogramar; nadie la actualiza el día de la cita.
  estado VARCHAR(20) NOT NULL DEFAULT 'agendada', -- agendada | cancelada | reprogramada
  creada_en TIMESTAMP NOT NULL DEFAULT now(),
  cancelada_en TIMESTAMP
);

CREATE TABLE notificaciones (
  id SERIAL PRIMARY KEY,
  cita_id INT NOT NULL REFERENCES citas(id),
  canal VARCHAR(10) NOT NULL, -- sms
  enviada_en TIMESTAMP NOT NULL,
  entregada BOOLEAN
);
