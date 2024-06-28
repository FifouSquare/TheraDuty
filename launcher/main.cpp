#include <QApplication>
#include <QWidget>
#include <QPushButton>
#include <QHBoxLayout>
#include <QStyle>
#include <QProcess>
#include <QMessageBox>
#include <QFile>
#include <QPixmap>

QPushButton *storeButton;
QPushButton *gamesButton;
QPushButton *formsButton;
QPushButton *game1;
QPushButton *game2;
QPushButton *buy1;
QPushButton *buy2;
QString buttonMenuStyle;
QString selectedButtonMenuStyle;

class LauncherWidget : public QWidget {
Q_OBJECT

public:
    ~LauncherWidget() override = default;

public slots:
    void launchApplication();
};

void LauncherWidget::launchApplication() {
    QString program = "/Users/delamonicavictor/CLionProjects/untitled/games/memo";
    QStringList arguments;

    if (!QFile::exists(program)) {
        QMessageBox::critical(this, "Error", "Application not found at: " + program);
        return;
    }

    bool started = QProcess::startDetached(program, arguments);
    if (!started) {
        QMessageBox::critical(this, "Error", "Failed to launch application");
    }
}

void onStoreButtonClicked(QPushButton *buttonClicked) {
    if (buttonClicked == storeButton) {
        storeButton->setStyleSheet(selectedButtonMenuStyle);
        gamesButton->setStyleSheet(buttonMenuStyle);
        formsButton->setStyleSheet(buttonMenuStyle);
        game1->hide();
        game2->hide();
        buy1->show();
        buy2->show();
    } else if (buttonClicked == gamesButton) {
        storeButton->setStyleSheet(buttonMenuStyle);
        gamesButton->setStyleSheet(selectedButtonMenuStyle);
        formsButton->setStyleSheet(buttonMenuStyle);
        game1->show();
        game2->show();
        buy1->hide();
        buy2->hide();
    } else if (buttonClicked == formsButton) {
        storeButton->setStyleSheet(buttonMenuStyle);
        gamesButton->setStyleSheet(buttonMenuStyle);
        formsButton->setStyleSheet(selectedButtonMenuStyle);
        game1->hide();
        game2->hide();
        buy1->hide();
        buy2->hide();
    }
}

int main(int argc, char *argv[]) {
    QApplication app(argc, argv);


    storeButton = new QPushButton("Store");
    gamesButton = new QPushButton("Games");
    formsButton = new QPushButton("Forms");

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
    QObject::connect(storeButton, &QPushButton::clicked, []() {
        onStoreButtonClicked(storeButton);
    });

    gamesButton->setFixedHeight(100);
    gamesButton->setFixedWidth(300);
    gamesButton->setStyleSheet(buttonMenuStyle);
    gamesButton->setCursor(Qt::PointingHandCursor);
    QObject::connect(gamesButton, &QPushButton::clicked, []() {
        onStoreButtonClicked(gamesButton);
    });

    formsButton->setFixedHeight(100);
    formsButton->setFixedWidth(300);
    formsButton->setStyleSheet(buttonMenuStyle);
    formsButton->setCursor(Qt::PointingHandCursor);
    QObject::connect(formsButton, &QPushButton::clicked, []() {
        onStoreButtonClicked(formsButton);
    });

    auto mainRow = new QHBoxLayout;
    auto layout = new QVBoxLayout;
    layout->addWidget(storeButton);
    layout->addWidget(gamesButton);
    layout->addWidget(formsButton);

    auto *storeColumn = new QVBoxLayout;
    storeColumn->setAlignment(Qt::AlignTop);
    auto demoGame = new QHBoxLayout;

    //GAME 1 : MEMO
    game1 = new QPushButton();
    QPixmap pic("../Pics/memory.png");
    game1->setIcon(pic);
    game1->setIconSize(QSize(200, 200));
    std::string game1Name = "Memory Game";
    game1->setText(QString::fromStdString(game1Name));

    //GAME 2 : BODY
    game2 = new QPushButton("Game 2");
    QPixmap pic2("../Pics/Tempo.png");
    game2->setIcon(pic2);
    game2->setIconSize(QSize(200, 200));
    std::string game2Name = "Body Game";
    game2->setText(QString::fromStdString(game2Name));


    buy1 = new QPushButton("Buy Game 3");
    buy2 = new QPushButton("Buy Game 4");
    demoGame->addWidget(game1);
    demoGame->addWidget(game2);
    demoGame->addWidget(buy1);
    demoGame->addWidget(buy2);
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