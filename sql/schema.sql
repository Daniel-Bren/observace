--
-- PostgreSQL database dump
--

\restrict LlEPUXnZZX1addxBUMGauXW8zvPTN49T4KjzyYJqsRglcLiS0Lpz199NVRYeDyk

-- Dumped from database version 17.11
-- Dumped by pg_dump version 17.11

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: despesas; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.despesas (
    id integer NOT NULL,
    municipio_id integer NOT NULL,
    exercicio_orcamento integer NOT NULL,
    data_referencia_doc integer NOT NULL,
    tipo_balancete character(1) NOT NULL,
    codigo_orgao character varying(2) NOT NULL,
    codigo_unidade_orcamentaria character varying(3) NOT NULL,
    codigo_funcao character varying(2) NOT NULL,
    codigo_subfuncao character varying(3) NOT NULL,
    codigo_programa character varying(4) NOT NULL,
    codigo_projeto_atividade character varying(1) NOT NULL,
    numero_projeto_atividade character varying(3) NOT NULL,
    numero_subprojeto_atividade character varying(4) NOT NULL,
    codigo_elemento_despesa character varying(8) NOT NULL,
    tipo_fonte character varying(1) NOT NULL,
    codigo_fonte character varying(9) NOT NULL,
    valor_fixado_orcamento_bal_despesa numeric(18,2),
    valor_suplementado_no_mes numeric(18,2),
    valor_suplementado_ate_mes numeric(18,2),
    valor_anulacoes_no_mes numeric(18,2),
    valor_empenhado_no_mes numeric(18,2),
    valor_empenhado_ate_mes numeric(18,2),
    valor_saldo_dotacao numeric(18,2),
    valor_pago_no_mes numeric(18,2),
    valor_pago_ate_mes numeric(18,2),
    valor_empenhado_pagar numeric(18,2),
    valor_anulacoes_dotacao_ate_mes numeric(18,2),
    valor_anulacoes_empenhos_no_mes numeric(18,2),
    valor_anulacoes_empenhos_ate_mes numeric(18,2),
    valor_liquidado_no_mes numeric(18,2),
    valor_liquidado_ate_mes numeric(18,2),
    valor_estornos_liquidacao_no_mes numeric(18,2),
    valor_estornos_liquidacao_ate_mes numeric(18,2),
    valor_estornos_pagos_no_mes numeric(18,2),
    valor_estornos_pagos_ate_mes numeric(18,2)
);


--
-- Name: despesas_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.despesas ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.despesas_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: municipios; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.municipios (
    id integer NOT NULL,
    codigo_ibge character varying(30) NOT NULL,
    nome character varying(100) NOT NULL,
    uf character varying(2) NOT NULL,
    codigo_tce character varying(30)
);


--
-- Name: municipios_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.municipios_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: municipios_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.municipios_id_seq OWNED BY public.municipios.id;


--
-- Name: receitas; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.receitas (
    id integer NOT NULL,
    municipio_id integer NOT NULL,
    codigo_orgao character varying(2) NOT NULL,
    exercicio_orcamento integer NOT NULL,
    codigo_unidade_orcamentaria character varying(3) NOT NULL,
    codigo_rubrica character varying(15) NOT NULL,
    tipo_fonte character varying(1) NOT NULL,
    codigo_fonte character varying(9) NOT NULL,
    data_referencia_doc integer NOT NULL,
    tipo_balancete character(1) NOT NULL,
    valor_previsto numeric(18,2) NOT NULL,
    arrecadacao_mes numeric(18,2) NOT NULL,
    arrecadacao_acumulada numeric(18,2) NOT NULL,
    anulacoes_mes numeric(18,2) NOT NULL,
    anulacoes_acumuladas numeric(18,2) NOT NULL
);


--
-- Name: receitas_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.receitas ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.receitas_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: municipios id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.municipios ALTER COLUMN id SET DEFAULT nextval('public.municipios_id_seq'::regclass);


--
-- Name: despesas despesas_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.despesas
    ADD CONSTRAINT despesas_pkey PRIMARY KEY (id);


--
-- Name: municipios municipios_codigo_ibge_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.municipios
    ADD CONSTRAINT municipios_codigo_ibge_key UNIQUE (codigo_ibge);


--
-- Name: municipios municipios_codigo_tce_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.municipios
    ADD CONSTRAINT municipios_codigo_tce_key UNIQUE (codigo_tce);


--
-- Name: municipios municipios_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.municipios
    ADD CONSTRAINT municipios_pkey PRIMARY KEY (id);


--
-- Name: receitas receitas_municipio_id_codigo_orgao_exercicio_orcamento_codi_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.receitas
    ADD CONSTRAINT receitas_municipio_id_codigo_orgao_exercicio_orcamento_codi_key UNIQUE (municipio_id, codigo_orgao, exercicio_orcamento, codigo_unidade_orcamentaria, codigo_rubrica, tipo_fonte, codigo_fonte, data_referencia_doc);


--
-- Name: receitas receitas_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.receitas
    ADD CONSTRAINT receitas_pkey PRIMARY KEY (id);


--
-- Name: despesas uq_despesas_posicao; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.despesas
    ADD CONSTRAINT uq_despesas_posicao UNIQUE (municipio_id, exercicio_orcamento, data_referencia_doc, tipo_balancete, codigo_orgao, codigo_unidade_orcamentaria, codigo_funcao, codigo_subfuncao, codigo_programa, codigo_projeto_atividade, numero_projeto_atividade, numero_subprojeto_atividade, codigo_elemento_despesa, tipo_fonte, codigo_fonte);


--
-- Name: despesas despesas_municipio_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.despesas
    ADD CONSTRAINT despesas_municipio_id_fkey FOREIGN KEY (municipio_id) REFERENCES public.municipios(id);


--
-- Name: receitas receitas_municipio_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.receitas
    ADD CONSTRAINT receitas_municipio_id_fkey FOREIGN KEY (municipio_id) REFERENCES public.municipios(id);


--
-- PostgreSQL database dump complete
--

\unrestrict LlEPUXnZZX1addxBUMGauXW8zvPTN49T4KjzyYJqsRglcLiS0Lpz199NVRYeDyk