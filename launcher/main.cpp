#include <QApplication>
#include <QWidget>
#include <QPushButton>
#include <QHBoxLayout>
#include <QStyle>
#include <QProcess>
#include <QMessageBox>
#include <QFile>
#include <QLabel>
#include <QPixmap>
#include <QPainter>
#include <__filesystem/operations.h>
#include <QToolButton>

QPushButton *storeButton;
QPushButton *contactButton;
QPushButton *gamesButton;
QPushButton *formsButton;
QPushButton *game1;
QPushButton *game2;
QPushButton *buy1;
QPushButton *buy2;
QPushButton *tempoButton;
QString buttonMenuStyle;
QString selectedButtonMenuStyle;

class VerticalIconButton : public QPushButton
{
public:
    VerticalIconButton(const QString &text, const QIcon &icon, QWidget *parent = nullptr)
            : QPushButton(parent)
    {
        setText(text);
        setIcon(icon);
        setIconSize(QSize(200, 200));
    }

protected:
    void paintEvent(QPaintEvent *event) override
    {
        QPainter painter(this);
        QSize iconSize = this->iconSize();
        QPixmap pixmap = icon().pixmap(iconSize);

        int iconX = (width() - iconSize.width()) / 2;
        int iconY = 0;
        int textX = 0;
        int textY = iconSize.height() + 10; // Adding a small space between icon and text

        painter.drawPixmap(iconX, iconY, pixmap);
        painter.drawText(QRect(textX, textY, width(), height() - iconSize.height()), Qt::AlignCenter, text());

        // Call base class implementation to handle other aspects
        QPushButton::paintEvent(event);
    }
};

class LauncherWidget : public QWidget {
Q_OBJECT

public:
    ~LauncherWidget() override = default;

public slots:

    void launchApplication(const QString &game, const std::string support);
};

void LauncherWidget::launchApplication(const QString &game, const std::string support) {
    QStringList arguments;

    if (!QFile::exists(game)) {
        QMessageBox::critical(this, "Error", "Application not found at: " + game);
        return;
    }
    bool started;
    QStringList command;
    if (support == "mac") {
        command << "-a";
        command << game.split("/").last().split(".").first();
        command << game;
        started = QProcess::startDetached("open", command);
    } else if (support == "python"){
        started = QProcess::startDetached(game, arguments);
    } else {
        command << game;
        started = QProcess::startDetached("/bin/sh", command);
    }
    if (!started) {
        QMessageBox::critical(this, "Error", "Failed to launch application");
    }
}

void onStoreButtonClicked(QPushButton *buttonClicked) {
    if (buttonClicked == storeButton) {
        storeButton->setStyleSheet(selectedButtonMenuStyle);
        gamesButton->setStyleSheet(buttonMenuStyle);
        formsButton->setStyleSheet(buttonMenuStyle);
        contactButton->setStyleSheet(buttonMenuStyle);
        game1->hide();
        game2->hide();
        buy1->show();
        buy2->show();
        tempoButton->hide();
    } else if (buttonClicked == gamesButton) {
        storeButton->setStyleSheet(buttonMenuStyle);
        gamesButton->setStyleSheet(selectedButtonMenuStyle);
        formsButton->setStyleSheet(buttonMenuStyle);
        contactButton->setStyleSheet(buttonMenuStyle);
        game1->show();
        game2->show();
        buy1->hide();
        buy2->hide();
        tempoButton->hide();
    } else if (buttonClicked == formsButton) {
        storeButton->setStyleSheet(buttonMenuStyle);
        gamesButton->setStyleSheet(buttonMenuStyle);
        formsButton->setStyleSheet(selectedButtonMenuStyle);
        contactButton->setStyleSheet(buttonMenuStyle);
        game1->hide();
        game2->hide();
        buy1->hide();
        buy2->hide();
        tempoButton->show();
    } else if (buttonClicked == contactButton) {
        storeButton->setStyleSheet(buttonMenuStyle);
        gamesButton->setStyleSheet(buttonMenuStyle);
        formsButton->setStyleSheet(buttonMenuStyle);
        contactButton->setStyleSheet(selectedButtonMenuStyle);
        game1->hide();
        game2->hide();
        buy1->hide();
        buy2->hide();
        tempoButton->show();
    }
}

int main(int argc, char *argv[]) {
    QApplication app(argc, argv);


    storeButton = new QPushButton("Store");
    gamesButton = new QPushButton("Games");
    formsButton = new QPushButton("Forms");
    contactButton = new QPushButton("Contact");

    QLabel *Logo = new QLabel("Thera Duty");
    QPixmap logo = QPixmap("../Pics/logo.png");
    Logo->setPixmap(logo);
    Logo->setFixedSize(120, 120);
    Logo->setPixmap(logo);


    buttonMenuStyle = "QPushButton { "
                      "border-top-left-radius: 20px; "
                      "border-bottom-left-radius: 24px; "
                      "padding: 5px; "
                      "opacity: 50%; "
                      "background-color: #3C3C3C; "
                      //a "background-color: #6A6A6A; "
                      "}";
    selectedButtonMenuStyle = "QPushButton { "
                              "border-top-left-radius: 20px; "
                              "border-bottom-left-radius: 24px; "
                              "padding: 5px; "
                              "opacity: 50%; "
                              "background-color: #6A6A6A; "
                              "}";

    LauncherWidget window;
    window.setWindowTitle("Thera Duty");
    window.setStyleSheet("background-color: #3C3C3C;");
    window.setFixedSize(1000, 800);

    storeButton->setFixedHeight(100);
    storeButton->setFixedWidth(300);
    storeButton->setStyleSheet(selectedButtonMenuStyle);
    storeButton->setCursor(Qt::PointingHandCursor);
    QIcon storeIcon("../assets/icons/menu/Store.png");
    storeButton->setIcon(storeIcon);
    QObject::connect(storeButton, &QPushButton::clicked, []() {
        onStoreButtonClicked(storeButton);
    });

    gamesButton->setFixedHeight(100);
    gamesButton->setFixedWidth(300);
    gamesButton->setStyleSheet(buttonMenuStyle);
    gamesButton->setCursor(Qt::PointingHandCursor);
    QIcon gameIcon("../assets/icons/menu/Game.png");
    gamesButton->setIcon(gameIcon);
    QObject::connect(gamesButton, &QPushButton::clicked, []() {
        onStoreButtonClicked(gamesButton);
    });

    formsButton->setFixedHeight(100);
    formsButton->setFixedWidth(300);
    formsButton->setStyleSheet(buttonMenuStyle);
    formsButton->setCursor(Qt::PointingHandCursor);
    QIcon formsIcon("../Pics/livre.png");
    formsButton->setIcon(formsIcon);
    QObject::connect(formsButton, &QPushButton::clicked, []() {
        onStoreButtonClicked(formsButton);
    });

    contactButton->setFixedHeight(100);
    contactButton->setFixedWidth(300);
    contactButton->setStyleSheet(buttonMenuStyle);
    contactButton->setCursor(Qt::PointingHandCursor);
    QIcon contactIcon("../Pics/contact.png");
    contactButton->setIcon(contactIcon);
    QObject::connect(contactButton, &QPushButton::clicked, []() {
        onStoreButtonClicked(contactButton);
    });

    auto mainRow = new QHBoxLayout;
    auto layout = new QVBoxLayout;
    auto rowLogo = new QHBoxLayout;
    auto rowcontact = new QHBoxLayout;

    rowLogo->setAlignment(Qt::AlignCenter);
    rowLogo->addWidget(Logo);

    rowcontact->addWidget(contactButton);
    rowcontact->setAlignment(Qt::AlignBottom);

    layout->addLayout(rowLogo);
    layout->addWidget(storeButton);
    layout->addWidget(gamesButton);
    layout->addWidget(formsButton);
    layout->addLayout(rowcontact);

    auto *storeColumn = new QVBoxLayout;
    storeColumn->setAlignment(Qt::AlignTop);
    auto demoGame = new QHBoxLayout;


    QString tools = "../../test.sh";
    // GAME 1 : MEMO
    game1 = new VerticalIconButton("Memory Game", QIcon("../assets/icons/games/memory.png"));
    QString path1 = "../games/memo";

    QObject::connect(game1, &QPushButton::clicked, &window, [&window, path1, tools]() {
        window.launchApplication(tools, "");
        window.launchApplication(path1, "python");
    });

    //GAME 2 : BODY
    game2 = new QPushButton("Memory Godot");
    QString path2 = "../games/Memory.dmg";
    QObject::connect(game2, &QPushButton::clicked, &window, [&window, path2, tools]() {
        window.launchApplication(tools, "");
        window.launchApplication(path2, "mac");
    });
    QPixmap pic2("../assets/icons/games/memory.png");
    game2->setIcon(pic2);
    game2->setIconSize(QSize(200, 200));


    buy1 = new QPushButton("Buy Game 3");
    buy2 = new QPushButton("Buy Game 4");
    tempoButton = new QPushButton();
    demoGame->addWidget(game1);
    demoGame->addWidget(game2);
    demoGame->addWidget(buy1);
    demoGame->addWidget(buy2);
    demoGame->addWidget(tempoButton);
    game1->hide();
    game2->hide();
    storeColumn->addLayout(demoGame);
    mainRow->addLayout(layout);
    mainRow->addLayout(storeColumn);


    window.setLayout(mainRow);

    window.resize(1000, 800);
    window.show();

    return QApplication::exec();
}

#include "main.moc"