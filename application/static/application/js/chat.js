class Message extends React.Component {

    render() {
        let d1class = 'row mb-3';
        let d2class = 'col-8 p-3 rounded bg-warning align-self-start';

        if (this.props.person !== 'bot') {
            d1class = 'row mb-3 justify-content-end';
            d2class = 'col-8 p-3 rounded bg-info text-light text-right';
        }

        return (
            <div className={d1class}>
                <div className={d2class}
                     dangerouslySetInnerHTML={{__html: this.props.text}}>
                </div>
            </div>
        );
    }
}

class Dialog extends React.Component {

    scrollToBottom = () => {
      this.messagesEnd.scrollIntoView({ behavior: "smooth" });
    };

    componentDidMount() {
      this.scrollToBottom();
    }

    componentDidUpdate() {
      this.scrollToBottom();
    }

    renderMessages() {
        return this.props.messages.map((text, i) => {
            let person = 'human';

            if (i%2 !== 0) {
                person = 'bot';
            }

            return (
                <Message text={text} key={i.toString()} person={person} />
            );
        });
    }

    render() {
        return (
            <div className="row align-items-center">
                <div className="col-12 px-5">
                    <div className="container-fluid">
                        {this.renderMessages()}
                    </div>
                    <div style={{ float:"left", clear: "both" }}
                         ref={(el) => { this.messagesEnd = el; }}>
                    </div>
                </div>
            </div>
        );
    }
}

class Painel extends React.Component {

    constructor(props) {
        super(props);
        this.state = {message:''};
    }

    sendMessage() {
        if (this.state.message !== '') {
            this.props.addMessage(this.state.message);
            const {addMessage} = this.props;

            fetch('/graphql', {
                headers: {"Content-Type": "application/json; charset=utf-8"},
                method: 'POST',
                body: '{"query":"query {message(chat:\\"' +
                    this.props.chatId + '\\", text:\\"' +
                    this.state.message + '\\")}"}'
            })
            .then(response => response.json())
            .then(response => {
                addMessage(
                    response.data.message.replace(/(?:\r\n|\r|\n)/g, '<br />')
                );
            });

            this.setState({message:''});
        }
    }

    onKeyPress(ev) {
        if (ev.key === 'Enter') {
            this.sendMessage()
        }
    }

    onChange(ev) {
        this.setState({message: ev.target.value})
    }

    render() {
        return (
            <div className="row fixed-bottom bg-info p-4">
                <div className="col-12 px-3">
                    <div className="input-group">
                        <input type="text" className="form-control"
                           placeholder="type your message here..."
                           aria-label="type your message here..." aria-describedby="button-send"
                           value={this.state.message}
                           onKeyPress={(ev) => this.onKeyPress(ev)}
                           onChange={(ev) => this.onChange(ev)}/>
                        <div className="input-group-append">
                            <button className="btn btn-success" type="button" id="button-send"
                                    onClick={() => this.sendMessage()}>Enviar</button>
                        </div>
                    </div>
                </div>
            </div>
        );
    }
}

class Chat extends React.Component {

    token = null;

    constructor (props) {
        super(props);
        this.state = {
            messages: [],
        };
    };

    static rand () {
        return Math.random().toString(36).substr(2); // remove `0.`
    };

    static genToken () {
        return Chat.rand() + Chat.rand(); // to make it longer
    };

    getToken () {
        if (this.token == null) {
            this.token = Chat.genToken()
        }

        return this.token
    };

    addMessage (message) {
        let messages = this.state.messages;
        messages.push(message);
        this.setState({
            messages,
        });
    };

    render() {
        return (
            <React.Fragment>
                <Dialog messages={this.state.messages} />
                <Painel addMessage={(msg) => this.addMessage(msg)} chatId={this.getToken()}/>
            </React.Fragment>
        );
    }
}


ReactDOM.render(
    <Chat />,
    document.querySelector('#application-chat')
);