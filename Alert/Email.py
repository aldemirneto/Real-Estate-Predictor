from email import encoders
from email.mime.base import MIMEBase
from Log.Logging import Logging
from config.ConfigManager import ConfigManager
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText



class EmailSender:
    def __init__(self,  mensagem, destinatario):
        self.remetente = None
        self.senha = None
        self.mensagem = mensagem
        self.destinatario = destinatario
        self._preencher_credenciais()



    def _preencher_credenciais(self):
        credenciais = ConfigManager().get_config()
        self.remetente = credenciais['remetente']['usuario']
        self.senha = credenciais['remetente']['senha']

    def criar_email(self):
        msg = MIMEMultipart()
        msg['Subject'] = 'ALERTA de Imóveis Atendido - Confira  as Novas Listagens que correspondem  aos Seus Critérios'
        msg['To'] = self.destinatario
        msg['From'] = self.remetente
        msg.attach(MIMEText(self.mensagem, 'html'))
        return msg

    def _criar_conexao(self):
        # Criar um objeto SMTP e se conectar ao servidor de e-mail
        servidor = smtplib.SMTP("smtp.office365.com", 587)
        #
        servidor.starttls()
        servidor.login(self.remetente, self.senha)
        return servidor

    def _df_to_HTML(self):
        # Estilos CSS para a mensagem
        css_styles = """
        <style>
            body { font-family: Arial, sans-serif; }
            .property-details { margin-bottom: 20px; }
            .property-details h3 { margin: 0 0 10px 0; color: #333; }
            .property-details ul { list-style: none; padding: 0; margin: 0; }
            .property-details ul li { margin: 5px 0; }
            .footer { margin-top: 20px; }
        </style>
        """

        # Inicialize uma lista vazia para armazenar os detalhes de cada imóvel
        properties_html = []
        i=0
        # Iterar sobre cada linha no DataFrame
        for index, row in self.mensagem.iterrows():
            i+=1
            property_details = f"""
                <div class="property-details">
                    <h3>🏠 {i}</h3>
                    <ul>
                        <li>Tipo: {row['tipo']}</li>
                        <li>Localização: {row['bairro']}</li>
                        <li>Preço: R$ {row['preco']}</li>
                        <li>Quartos: {row['quartos']}</li>
                        <li>Banheiros: {row['banheiros']}</li>
                        <li>Área: {row['area']}</li>
                        <li>Vagas: {row['vagas']}</li>
                        
                    <li>Link do Anúncio: <a href="{row['link']}">Clique aqui</a></li>
                    </ul>
                </div>
            """
            properties_html.append(property_details)

        # Junte todos os detalhes dos imóveis em uma única string
        properties_html_string = "\n".join(properties_html)

        # Construa a mensagem HTML final
        self.mensagem = f"""\
                        <html>
                          <head>
                            {css_styles}
                          </head>
                          <body>
                            <p>Olá Usuário,<br>
                               Esperamos que esteja tudo bem com você!<br>
                               Estamos felizes em informar que encontramos novas listagens de imóveis que atendem aos critérios do seu alerta. Abaixo estão os detalhes:<br>
                            </p>
                            {properties_html_string}
                            <div class="footer">
                                <p>
                                    Para mais informações ou para agendar uma visita, você pode clicar diretamente no link do anúncio.<br>
                                    Se você tiver alguma dúvida ou precisar de mais informações, fique à vontade para nos contatar.<br>
                                    <br>
                                    Atenciosamente,<br>
                                    Equipe
                                </p>
                            </div>
                          </body>
                        </html>
                        """




    def envio(self):
        servidor = self._criar_conexao()
        self._df_to_HTML()
        email = self.criar_email()

        servidor.sendmail(self.remetente, self.destinatario, email.as_string())
        servidor.quit()
        print("E-mail enviado com sucesso!")
