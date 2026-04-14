from bird.microjobs import MicroJobServer

server = MicroJobServer()
app = server.setup_job_app()

if __name__ == '__main__':
    app.start_job_processing()